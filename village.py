# village.py
import sqlite3
import random
from datetime import datetime, timedelta  # Add this import at the top of the file

class Village:
    def __init__(self, db_path='village.db'):
        self.db_path = db_path
        self.locations = ["Marketplace", "Town Square", "Bakery", "Farmhouse", "River Bank"]
        self.current_time = datetime.now()

    def add_npc(self, npc):
        # Assign a random starting location if not set
        if npc.current_location is None:
            npc.current_location = random.choice(self.locations)
            self.update_npc_location(npc)

    def move_npc(self, npc):
        old_location = npc.current_location
        new_location = random.choice([loc for loc in self.locations if loc != old_location])
        npc.current_location = new_location
        self.update_npc_location(npc)
        return new_location

    def update_npc_location(self, npc):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE npcs
            SET current_location = ?
            WHERE id = ?
        ''', (npc.current_location, npc.get_npc_id()))
        conn.commit()
        conn.close()

    def get_current_time_str(self):
        return self.current_time.strftime("%Y-%m-%d %H:%M:%S")

    def advance_time(self, delta_seconds=60):
        self.current_time += timedelta(seconds=delta_seconds)
