# capture/flow_tracker.py

import time
from collections import defaultdict

class FlowTracker:
    def __init__(self, flow_timeout=60):
        self.flow_timeout = flow_timeout
        self.active_flows = {}
        self.completed_flows = []

    def _flow_key(self, packet):
        return (
            packet["src_ip"],
            packet["dst_ip"],
            packet["src_port"],
            packet["dst_port"],
            packet["protocol"]
        )

    def update_flow(self, packet):
        key = self._flow_key(packet)
        now = packet["timestamp"]

        if key not in self.active_flows:
            self.active_flows[key] = {
                "src_ip": packet["src_ip"],
                "dst_ip": packet["dst_ip"],
                "src_port": packet["src_port"],
                "dst_port": packet["dst_port"],
                "protocol": packet["protocol"],
                "start_time": now,
                "last_seen": now,
                "packets": 1,
                "bytes": packet["size"],
                "inter_arrival_times": []
            }
            return

        flow = self.active_flows[key]
        flow["inter_arrival_times"].append(now - flow["last_seen"])
        flow["last_seen"] = now
        flow["packets"] += 1
        flow["bytes"] += packet["size"]

        self._expire_flows(now)

    def _expire_flows(self, current_time):
        expired_keys = []

        for key, flow in self.active_flows.items():
            if current_time - flow["last_seen"] > self.flow_timeout:
                flow["duration"] = flow["last_seen"] - flow["start_time"]
                self.completed_flows.append(flow)
                expired_keys.append(key)

        for key in expired_keys:
            del self.active_flows[key]

    def get_completed_flows(self):
        flows = self.completed_flows[:]
        self.completed_flows.clear()
        return flows
    
    def get_active_flows(self):
        """
        Return a snapshot of active flows without expiring them
        """
        return list(self.active_flows.values())

