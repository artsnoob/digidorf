# simulation.py
import time
from datetime import timedelta
import random
from village import Village
from npc import NPC

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
    NPC.initialize_database()  # Add this line
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

    for _ in range(25):  # Simulate 10 time steps
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
                print_npc_action(npc, action)
        
        # Move NPCs (30% chance)
        for npc in [npc1, npc2]:
            if random.random() < 0.3:
                old_location = npc.current_location
                new_location = village.move_npc(npc)
                print_movement(npc, old_location, new_location)
        
        village.advance_time(60)  # Advance time by 60 seconds
        time.sleep(0.5)  # Pause for 1 second between time steps

    print_separator()
    print("🏁 Simulation ended.")

if __name__ == "__main__":
    main()
