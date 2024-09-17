import subprocess
import json
import time
from datetime import datetime
import random
from village import Village

class NPC:
    def __init__(self, name, personality, backstory):
        self.name = name
        self.personality = personality
        self.backstory = backstory
        self.current_location = None
        self.short_term_memory = []  # Limited to recent interactions
        self.long_term_memory = []   # Persistent storage of all interactions
        self.short_term_memory_limit = 20  # Adjust as needed
        self.interaction_log = []  # Initialize the interaction_log
        self.load_long_term_memory()

    def load_long_term_memory(self):
        try:
            with open(f'{self.name}_long_term_memory.json', 'r') as f:
                self.long_term_memory = json.load(f)
        except FileNotFoundError:
            self.long_term_memory = []

    def save_long_term_memory(self):
        with open(f'{self.name}_long_term_memory.json', 'w') as f:
            json.dump(self.long_term_memory, f, indent=4)

    def add_to_memory(self, entry):
        self.short_term_memory.append(entry)
        if len(self.short_term_memory) > self.short_term_memory_limit:
            self.transfer_to_long_term_memory()

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

    def log_interaction(self, user_input, npc_response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'user': user_input,
            'npc': npc_response
        }
        self.interaction_log.append(log_entry)
        
        with open('interaction_log.json', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

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
        return action

    def log_action(self, action):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'npc': self.name,
            'location': self.current_location,
            'action': action
        }
        self.interaction_log.append(log_entry)
        
        with open('actions.json', 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')

def print_separator():
    print("\n" + "="*50 + "\n")

def print_time_header(village):
    print(f"🕒 Time: {village.get_current_time_str()}")
    print("-" * 20)

def print_npc_action(npc, action):
    location_emoji = {
        "Marketplace": "🏪",
        "Town Square": "🏛️",
        "Bakery": "🥖",
        "Farmhouse": "🏡",
        "River Bank": "🏞️"
    }
    emoji = location_emoji.get(npc.current_location, "📍")
    print(f"{emoji} {npc.name} at {npc.current_location}:")
    print(f"   {action}")
    print()

def print_interaction(speaker, listener, response):
    print(f"💬 {speaker.name} to {listener.name}:")
    print(f"   {response}")
    print()

def print_movement(npc, old_location, new_location):
    print(f"🚶 {npc.name} moved from {old_location} to {new_location}")
    print()

def main():
    village = Village()
    
    npc1 = NPC(
        name="Evelyn",
        personality="friendly baker",
        backstory="Runs the local bakery, loves chatting."
    )
    
    npc2 = NPC(
        name="George",
        personality="grumpy farmer",
        backstory="50-year farming veteran, outspoken."
    )
    
    village.add_npc(npc1)
    village.add_npc(npc2)

    print("🏘️ Village Simulation Starting")
    print(f"🕒 Time: {village.get_current_time_str()}")
    print(f"👩‍🍳 {npc1.name} at {npc1.current_location}")
    print(f"👨‍🌾 {npc2.name} at {npc2.current_location}")

    for _ in range(10):  # Simulate 10 time steps
        print_separator()
        print_time_header(village)
        
        if npc1.current_location == npc2.current_location:
            speaker, listener = random.sample([npc1, npc2], 2)
            
            initial_statement = speaker.interact_with(listener)
            print_interaction(speaker, listener, initial_statement)
            
            reaction = listener.react_to(speaker, initial_statement)
            print_interaction(listener, speaker, reaction)
        else:
            for npc in [npc1, npc2]:
                action = npc.perform_action()
                npc.log_action(action)  # Add this line if you want to keep separate action logs
                print_npc_action(npc, action)
        
        # Move NPCs (30% chance)
        for npc in [npc1, npc2]:
            if random.random() < 0.3:
                old_location = npc.current_location
                new_location = village.move_npc(npc)
                print_movement(npc, old_location, new_location)
        
        village.advance_time(1)
        time.sleep(1)  # Pause for 1 second between time steps

    print_separator()
    print("🏁 Simulation ended.")

if __name__ == "__main__":
    main()
