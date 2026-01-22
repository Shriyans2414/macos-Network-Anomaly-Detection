# features/feature_extractor.py

import numpy as np
from collections import Counter
from math import log2

class FeatureExtractor:
    def __init__(self):
        pass

    def _entropy(self, values):
        counts = Counter(values)
        total = sum(counts.values())
        return -sum(
            (count / total) * log2(count / total)
            for count in counts.values()
            if count > 0
        )

    def extract(self, flows):
        """
        Extracts features from a list of flows
        """
        if not flows:
            return None

        durations = [
            f["last_seen"] - f["start_time"]
            for f in flows
            if f["last_seen"] > f["start_time"]
   ]

        packets = [f["packets"] for f in flows]
        bytes_ = [f["bytes"] for f in flows]
        dst_ips = [f["dst_ip"] for f in flows]
        dst_ports = [f["dst_port"] for f in flows]
        inter_arrivals = [
            t for f in flows for t in f["inter_arrival_times"]
        ]

        features = {
            # Volume & count
            "active_connections": len(flows),
            "mean_packets_per_flow": np.mean(packets),
            "mean_bytes_per_flow": np.mean(bytes_),

            # Duration
            "avg_flow_duration": np.mean(durations) if durations else 0,
            "max_flow_duration": np.max(durations) if durations else 0,

            # Behavioral
            "unique_dst_ip_count": len(set(dst_ips)),
            "unique_dst_port_count": len(set(dst_ports)),

            # Distributional
            "dst_ip_entropy": self._entropy(dst_ips),
            "dst_port_entropy": self._entropy(dst_ports),

            # Timing
            "mean_inter_arrival": np.mean(inter_arrivals) if inter_arrivals else 0,
            "std_inter_arrival": np.std(inter_arrivals) if inter_arrivals else 0,
        }

        return features
