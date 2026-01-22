# features/window_aggregator.py

import time
from collections import deque

class WindowAggregator:
    def __init__(self, window_size=60):
        self.window_size = window_size
        self.windows = deque()

    def add_flows(self, flows):
        """
        Add completed flows to sliding windows
        """
        for flow in flows:
            self.windows.append(flow)

    def get_window(self):
        """
        Returns flows within the current time window
        """
        if not self.windows:
            return []

        current_time = time.time()
        window_flows = []

        while self.windows:
            flow = self.windows[0]
            if current_time - flow["last_seen"] <= self.window_size:
                window_flows.append(flow)
                self.windows.popleft()
            else:
                self.windows.popleft()

        return window_flows
