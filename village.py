from datetime import datetime, timedelta
import random

class Village:
    def __init__(self):
        self.locations = [
            "Town Square",
            "Bakery",
            "Marketplace",
            "Farmhouse",
            "River Bank"
        ]
        self.npcs = {}
        self.current_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)  # Start at 6 AM

    def add_npc(self, npc):
        self.npcs[npc.name] = npc
        # Assign a random starting location
        npc.current_location = random.choice(self.locations)

    def advance_time(self, hours=1):
        self.current_time += timedelta(hours=hours)

    def get_current_time_str(self):
        return self.current_time.strftime("%H:%M")

    def get_npc_locations(self):
        return {name: npc.current_location for name, npc in self.npcs.items()}

    def get_npcs_at_location(self, location):
        return [npc for npc in self.npcs.values() if npc.current_location == location]

    def move_npc(self, npc):
        new_location = random.choice([loc for loc in self.locations if loc != npc.current_location])
        npc.current_location = new_location
