class DroneAdapter:
    def send_waypoints(self, waypoints):
        print("Sending waypoints:", waypoints)

    def start_mission(self, mission_id: int):
        print(f"Starting mission {mission_id}")
