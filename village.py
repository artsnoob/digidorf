from datetime import datetime, timedelta
import random

class Village:
    def __init__(self):
        self.current_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)  # Start at 6 AM
        self.locations = ["Marketplace", "Town Square", "Bakery", "Farmhouse", "River Bank"]
        self.npcs = []

    def add_npc(self, npc):
        self.npcs.append(npc)
        # Assign a random starting location
        npc.current_location = random.choice(self.locations)

    def move_npc(self, npc):
        available_locations = [loc for loc in self.locations if loc != npc.current_location]
        new_location = random.choice(available_locations)
        npc.current_location = new_location
        return new_location

    def get_current_time_str(self):
        return self.current_time.strftime("%Y-%m-%d %H:%M:%S")

    def advance_time(self, hours):
        self.current_time += timedelta(hours=hours)

    def get_npc_locations(self):
        return {npc.name: npc.current_location for npc in self.npcs}

    def get_npcs_at_location(self, location):
        return [npc for npc in self.npcs if npc.current_location == location]
