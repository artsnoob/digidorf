# npc.py
import sqlite3
from datetime import datetime
import subprocess
import json
import random  # Add this import at the top of the file

class NPC:
    db_path = 'village.db'  # Class-level attribute for database path

    def __init__(self, name, personality, backstory):
        self.name = name
        self.personality = personality
        self.backstory = backstory
        self.current_location = "Town Square"  # Default location
        self.short_term_memory = []
        self.long_term_memory = []
        self.initialize_database()
        self.initialize_npc()
        self.load_long_term_memory()
        self.id = self.get_npc_id()  # Set the id attribute

    @classmethod
    def initialize_database(cls):
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        
        # Create the npcs table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS npcs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            personality TEXT NOT NULL,
            backstory TEXT NOT NULL,
            current_location TEXT NOT NULL
        )
        ''')
        
        # Create the long_term_memory table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY,
            npc_name TEXT NOT NULL,
            memory TEXT NOT NULL
        )
        ''')
        
        # Drop and recreate the interactions table
        cursor.execute('DROP TABLE IF EXISTS interactions')
        cursor.execute('''
        CREATE TABLE interactions (
            id INTEGER PRIMARY KEY,
            speaker_id INTEGER,
            listener_id INTEGER,
            interaction_type TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (speaker_id) REFERENCES npcs (id),
            FOREIGN KEY (listener_id) REFERENCES npcs (id)
        )
        ''')

        # Create the actions table
        cursor.execute('DROP TABLE IF EXISTS actions')
        cursor.execute('''
        CREATE TABLE actions (
            id INTEGER PRIMARY KEY,
            npc_id INTEGER,
            location TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (npc_id) REFERENCES npcs (id)
        )
        ''')
        
        conn.commit()
        conn.close()

    def initialize_npc(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Insert NPC into the database if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO npcs (name, personality, backstory, current_location)
            VALUES (?, ?, ?, ?)
        ''', (self.name, self.personality, self.backstory, self.current_location))
        conn.commit()
        conn.close()

    def get_npc_id(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM npcs WHERE name = ?', (self.name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def load_long_term_memory(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT memory FROM long_term_memory WHERE npc_name = ?', (self.name,))
        memories = cursor.fetchall()
        self.long_term_memory = [memory[0] for memory in memories]
        conn.close()

    def save_long_term_memory(self, memory):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO long_term_memory (npc_name, memory) VALUES (?, ?)', (self.name, memory))
        conn.commit()
        conn.close()

    def add_to_memory(self, entry, memory_type='short'):
        if memory_type == 'short':
            self.short_term_memory.append(entry)
        elif memory_type == 'long':
            self.long_term_memory.append(entry)
            self.save_long_term_memory(entry)

    def transfer_to_long_term_memory(self):
        # Transfer the oldest half of short-term memories to long-term
        transfer_count = len(self.short_term_memory) // 2
        transferred_memories = self.short_term_memory[:transfer_count]
        self.short_term_memory = self.short_term_memory[transfer_count:]
        
        # Summarize transferred memories before adding to long-term
        summary = self.summarize_memories(transferred_memories)
        self.long_term_memory.append(summary)
        self.save_long_term_memory()

    def summarize_memories(self, memories):
        # Use LLM to summarize memories
        prompt = f"""
        Summarize the following memories in a concise paragraph:
        {self.format_memory(memories)}
        Summary:
        """
        return self.call_llm(prompt)

    def generate_prompt(self, user_input):
        """
        Generates a prompt for the LLM based on the NPC's current state and memories.
        """
        summarized_long_term = self.summarize_long_term_memory()

        prompt = f"""
        You are {self.name}, a {self.personality}.
        Backstory: {self.backstory}
        Current mood: {self.get_current_mood()}
        
        Recent memories:
        {self.format_memory(self.short_term_memory)}
        
        Long-term memories (summarized):
        {summarized_long_term}
        
        Interaction with User:
        User: {user_input}
        {self.name}:
        """
        return prompt

    def summarize_long_term_memory(self):
        """
        Summarizes long-term memory to fit within context window constraints.
        """
        if not self.long_term_memory:
            return "No significant past interactions."

        # Simple summarization: concatenate and truncate to a reasonable length
        summary = " ".join(self.long_term_memory[-50:])  # Adjust the number as needed
        if len(summary) > 1000:  # Example character limit
            summary = summary[:1000] + "..."
        return summary

    def get_current_mood(self):
        """
        Placeholder for mood determination logic.
        """
        # Implement mood based on interactions or other factors
        return "neutral"

    def format_memory(self, memory_list):
        """
        Formats memory lists into a readable string.
        """
        return "\n".join([f"- {mem}" for mem in memory_list])

    def call_llm(self, prompt):
        """
        Calls the local Ollama Phi3 model with the given prompt.
        Assumes Ollama can be invoked via command line and returns the output.
        """
        try:
            result = subprocess.run(
                ['ollama', 'run', 'phi3', prompt],
                capture_output=True,
                text=True,
                timeout=30  # seconds
            )
            if result.returncode != 0:
                print("Error calling LLM:", result.stderr)
                return "I'm sorry, I couldn't process that."
            return result.stdout.strip()
        except Exception as e:
            print("Exception during LLM call:", e)
            return "I'm sorry, something went wrong."

    def respond(self, user_input):
        # Update memories
        self.add_to_memory(f"User: {user_input}")
        prompt = self.generate_prompt(user_input)
        response = self.call_llm(prompt)
        self.add_to_memory(f"{self.name}: {response}")
        self.log_interaction(user_input, response)
        return response

    def log_interaction(self, action, details):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interactions (speaker_id, listener_id, interaction_type, content)
                VALUES (?, ?, ?, ?)
            ''', (self.id, None, action, details))
            conn.commit()

    def interact_with(self, other_npc, topic=None):
        if topic is None:
            topics = ["weather", "village news", "hobbies", "food", "family"]
            topic = random.choice(topics)
        
        prompt = f"""
        You are {self.name}, a {self.personality}.
        You're talking to {other_npc.name}, a {other_npc.personality}, about {topic}.
        Say something brief (5-10 words) to start the conversation.
        {self.name}:
        """
        
        response = self.call_llm(prompt)
        self.add_to_memory(f"Talked to {other_npc.name} about {topic}", memory_type='long')
        self.log_interaction(f"Talking to {other_npc.name}", response)
        return response

    def react_to(self, other_npc, other_npc_statement):
        prompt = f"""
        You are {self.name}, a {self.personality}.
        {other_npc.name} just said: "{other_npc_statement}"
        Respond briefly (5-10 words).
        {self.name}:
        """
        
        response = self.call_llm(prompt)
        self.add_to_memory(f"Reacted to {other_npc.name}", memory_type='long')
        self.log_interaction(f"Reacting to {other_npc.name}", response)
        return response

    def perform_action(self):
        prompt = f"""
        You are {self.name}, a {self.personality}.
        You are at the {self.current_location}.
        Describe a brief action or thought in 5-10 words.
        {self.name}:
        """
        action = self.call_llm(prompt)
        self.add_to_memory(f"Action: {action}")
        self.log_action(self.get_npc_id(), self.current_location, action)
        return action

    def log_action(self, npc_id, location, action):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO actions (npc_id, location, action)
                VALUES (?, ?, ?)
            ''', (npc_id, location, action))
            conn.commit()
