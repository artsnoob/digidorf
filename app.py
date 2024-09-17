# app.py
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit
import sqlite3
import time
from threading import Thread
import socket
from flask import Response
import json  # Add this import at the top of the file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

DB_PATH = 'village.db'

def get_npc_id(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM npcs WHERE name = ?', (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_npc_name(npc_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM npcs WHERE id = ?', (npc_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'Unknown'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/npcs', methods=['GET'])
def get_npcs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, personality, current_location FROM npcs')
    npcs = cursor.fetchall()
    conn.close()
    npc_list = [{'id': npc[0], 'name': npc[1], 'personality': npc[2], 'current_location': npc[3]} for npc in npcs]
    return jsonify(npc_list)

@app.route('/api/interactions', methods=['GET'])
def get_interactions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, npc_speaker_id, npc_listener_id, topic, content 
        FROM interactions 
        ORDER BY timestamp DESC 
        LIMIT 100
    ''')
    interactions = cursor.fetchall()
    conn.close()
    interaction_list = []
    for interaction in interactions:
        interaction_list.append({
            'timestamp': interaction[0],
            'speaker_id': interaction[1],
            'listener_id': interaction[2],
            'topic': interaction[3],
            'content': interaction[4]
        })
    return jsonify(interaction_list)

@app.route('/api/actions', methods=['GET'])
def get_actions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, npc_id, location, action 
        FROM actions 
        ORDER BY timestamp DESC 
        LIMIT 100
    ''')
    actions = cursor.fetchall()
    conn.close()
    action_list = []
    for action in actions:
        action_list.append({
            'timestamp': action[0],
            'npc_id': action[1],
            'location': action[2],
            'action': action[3]
        })
    return jsonify(action_list)

@app.route('/get_updates')
def get_updates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch NPCs
    cursor.execute('SELECT id, name, personality, current_location FROM npcs')
    npcs = [{'id': row[0], 'name': row[1], 'personality': row[2], 'current_location': row[3]} for row in cursor.fetchall()]
    
    # Fetch recent interactions
    cursor.execute('''
        SELECT timestamp, speaker_id, listener_id, interaction_type, content 
        FROM interactions 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    interactions = [
        {
            'timestamp': row[0],
            'speaker_id': row[1],
            'listener_id': row[2],
            'interaction_type': row[3],
            'content': row[4]
        } for row in cursor.fetchall()
    ]
    
    # Fetch recent actions
    cursor.execute('''
        SELECT timestamp, npc_id, location, action 
        FROM actions 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    actions = [
        {
            'timestamp': row[0],
            'npc_id': row[1],
            'location': row[2],
            'action': row[3]
        } for row in cursor.fetchall()
    ]
    
    conn.close()
    
    return jsonify({'npcs': npcs, 'interactions': interactions, 'actions': actions})

@app.route('/sse')
def sse():
    def event_stream():
        while True:
            time.sleep(10)  # Wait for 10 seconds
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                
                # Fetch NPCs
                cursor.execute('SELECT id, name, personality, current_location FROM npcs')
                npcs = [{'id': row[0], 'name': row[1], 'personality': row[2], 'current_location': row[3]} for row in cursor.fetchall()]
                
                # Fetch recent interactions
                cursor.execute('''
                    SELECT timestamp, speaker_id, listener_id, interaction_type, content 
                    FROM interactions 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                ''')
                interactions = [
                    {
                        'timestamp': row[0],
                        'speaker_id': row[1],
                        'listener_id': row[2],
                        'interaction_type': row[3],
                        'content': row[4]
                    } for row in cursor.fetchall()
                ]
                
                # Fetch recent actions
                cursor.execute('''
                    SELECT timestamp, npc_id, location, action 
                    FROM actions 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                ''')
                actions = [
                    {
                        'timestamp': row[0],
                        'npc_id': row[1],
                        'location': row[2],
                        'action': row[3]
                    } for row in cursor.fetchall()
                ]
            
            data = {'npcs': npcs, 'interactions': interactions, 'actions': actions}
            yield f"data: {json.dumps(data)}\n\n"
    
    return Response(event_stream(), content_type='text/event-stream')

def background_thread():
    """Send server generated events to clients."""
    with app.app_context():
        while True:
            time.sleep(10)  # Adjust as needed
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Fetch NPCs
            cursor.execute('SELECT id, name, personality, current_location FROM npcs')
            npcs = [{'id': row[0], 'name': row[1], 'personality': row[2], 'current_location': row[3]} for row in cursor.fetchall()]
            
            # Fetch recent interactions
            cursor.execute('''
                SELECT timestamp, speaker_id, listener_id, interaction_type, content 
                FROM interactions 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            interactions = [
                {
                    'timestamp': row[0],
                    'speaker_id': row[1],
                    'listener_id': row[2],
                    'interaction_type': row[3],
                    'content': row[4]
                } for row in cursor.fetchall()
            ]
            
            # Fetch recent actions
            cursor.execute('''
                SELECT timestamp, npc_id, location, action 
                FROM actions 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            actions = [
                {
                    'timestamp': row[0],
                    'npc_id': row[1],
                    'location': row[2],
                    'action': row[3]
                } for row in cursor.fetchall()
            ]
            
            conn.close()
            
            data = {'npcs': npcs, 'interactions': interactions, 'actions': actions}
            print("Emitting update:", data)
            socketio.emit('update', data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def print_db_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name in tables:
        print(f"\nTable: {table_name[0]}")
        cursor.execute(f"PRAGMA table_info({table_name[0]})")
        columns = cursor.fetchall()
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
    conn.close()

if __name__ == '__main__':
    print_db_schema()  # Add this line before running the app
    # Start the background thread
    thread = Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    
    # Try to run on port 5001, fall back to a random available port if it's in use
    port = 5001
    max_attempts = 5
    
    for attempt in range(max_attempts):
        try:
            socketio.run(app, host='0.0.0.0', port=port, debug=True, use_reloader=False)
            break
        except OSError:
            if attempt < max_attempts - 1:
                print(f"Port {port} is in use, trying another port...")
                # Find a random available port
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', 0))
                    port = s.getsockname()[1]
            else:
                print(f"Unable to find an available port after {max_attempts} attempts.")
                raise
