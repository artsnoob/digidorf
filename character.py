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
        self.memory = []
        self.interaction_log = []

    def generate_prompt(self, user_input):
        """
        Generates a prompt for the LLM based on the NPC's current state and memories.
        """
        prompt = f"""
        You are {self.name}, a {self.personality}.
        Backstory: {self.backstory}
        Current mood: {self.state['mood']}
        
        Short-term memories:
        {self.format_memory(self.short_term_memory)}
        
        Long-term memories:
        {self.format_memory(self.long_term_memory)}
        
        Interaction with User:
        User: {user_input}
        {self.name}:
        """
        return prompt

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
        self.memory.append(f"User: {user_input}")
        
        context = f"Your name is {self.name}. You are a {self.personality}. {self.backstory}\n"
        context += "Recent interactions:\n" + "\n".join(self.memory[-5:])
        
        prompt = f"{context}\n\nUser: {user_input}\n{self.name}:"

        response = self.call_llm(prompt)
        
        self.memory.append(f"{self.name}: {response}")
        
        if len(self.memory) > 10:
            self.memory = self.memory[-10:]
        
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

    def interact_with(self, other_npc):
        topics = ["weather", "village news", "hobbies", "food", "family"]
        topic = random.choice(topics)
        
        prompt = f"""
        You are {self.name}, a {self.personality}.
        You are talking to {other_npc.name}, who is a {other_npc.personality}.
        You are both at the {self.current_location}.
        Start a conversation about {topic}.
        Keep your response brief (1-2 sentences).
        {self.name}:
        """
        
        response = self.call_llm(prompt)
        
        self.log_interaction(f"Talking to {other_npc.name} about {topic}", response)
        
        return response

    def perform_action(self):
        prompt = f"""
        You are {self.name}, a {self.personality}.
        You are currently at the {self.current_location}.
        Describe a brief action or thought you have, related to your location or personality.
        Keep your response to 1-2 sentences.
        {self.name}:
        """
        action = self.call_llm(prompt)
        return action

    def log_action(self, action):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'npc': self.name,
            'location': self.current_location,
            'action': action
        }
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
        personality="friendly and curious baker",
        backstory="Evelyn grew up in the village, helping her family run the local bakery. She loves baking and enjoys chatting with the townsfolk."
    )
    
    npc2 = NPC(
        name="George",
        personality="grumpy but wise farmer",
        backstory="George has been farming in the village for over 50 years. He's seen it all and isn't afraid to speak his mind."
    )
    
    village.add_npc(npc1)
    village.add_npc(npc2)

    print("🏘️ Welcome to the Village Simulation!")
    print(f"🕒 The current time is {village.get_current_time_str()}.")
    print(f"👩‍🍳 {npc1.name} is at the {npc1.current_location}.")
    print(f"👨‍🌾 {npc2.name} is at the {npc2.current_location}.")
    print("Simulation starting...\n")

    for _ in range(10):  # Simulate 10 time steps
        print_separator()
        print_time_header(village)
        
        if npc1.current_location == npc2.current_location:
            print(f"👥 Both NPCs are at {npc1.current_location}")
            speaker, listener = random.sample([npc1, npc2], 2)
            
            response = speaker.interact_with(listener)
            print_interaction(speaker, listener, response)
            speaker.log_action(f"Interacted with {listener.name}: {response}")
            
            response = listener.interact_with(speaker)
            print_interaction(listener, speaker, response)
            listener.log_action(f"Responded to {speaker.name}: {response}")
        else:
            action1 = npc1.perform_action()
            print_npc_action(npc1, action1)
            npc1.log_action(action1)

            action2 = npc2.perform_action()
            print_npc_action(npc2, action2)
            npc2.log_action(action2)
        
        # Move NPCs
        for npc in [npc1, npc2]:
            if random.random() < 0.3:  # 30% chance to move
                old_location = npc.current_location
                village.move_npc(npc)
                print_movement(npc, old_location, npc.current_location)
                npc.log_action(f"Moved from {old_location} to {npc.current_location}")
        
        # Advance time
        village.advance_time(1)
        time.sleep(2)  # Pause for 2 seconds between time steps

    print_separator()
    print("🏁 Simulation ended.")

if __name__ == "__main__":
    main()
