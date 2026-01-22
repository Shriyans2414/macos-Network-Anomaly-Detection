# evaluation/evaluate_pcap.py

import os
import sys

# ------------------------------------------------------------------
# Fix Python imports (add project root to path)
# ------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ------------------------------------------------------------------
# Fix Scapy cache permission issues on macOS / Conda
# ------------------------------------------------------------------
os.environ["XDG_CACHE_HOME"] = "/tmp"
os.environ["SCAPY_CACHE"] = "0"

# ------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------
import numpy as np
from scapy.all import rdpcap, IP, TCP, UDP

from capture.flow_tracker import FlowTracker
from features.window_aggregator import WindowAggregator
from features.feature_extractor import FeatureExtractor
from models.feature_vectorizer import vectorize
from models.isolation_forest import IsolationForestModel


# ------------------------------------------------------------------
# Helper: Convert Scapy packet → internal packet dict
# ------------------------------------------------------------------
def scapy_to_packet_dict(pkt):
    if not pkt.haslayer(IP):
        return None

    protocol = "OTHER"
    src_port = 0
    dst_port = 0

    if pkt.haslayer(TCP):
        protocol = "TCP"
        src_port = pkt[TCP].sport
        dst_port = pkt[TCP].dport
    elif pkt.haslayer(UDP):
        protocol = "UDP"
        src_port = pkt[UDP].sport
        dst_port = pkt[UDP].dport

    return {
        "src_ip": pkt[IP].src,
        "dst_ip": pkt[IP].dst,
        "src_port": src_port,
        "dst_port": dst_port,
        "protocol": protocol,
        "timestamp": pkt.time,
        "size": len(pkt)
    }


# ------------------------------------------------------------------
# Helper: Force-expire remaining flows (offline evaluation fix)
# ------------------------------------------------------------------
def flush_active_flows(flow_tracker: FlowTracker):
    # Force all active flows to expire
    flow_tracker._expire_flows(float("inf"))
    return flow_tracker.get_completed_flows()


# ------------------------------------------------------------------
# PCAP Evaluation Function
# ------------------------------------------------------------------
def evaluate_pcap(pcap_path: str, model: IsolationForestModel):
    packets = rdpcap(pcap_path)

    flow_tracker = FlowTracker()
    aggregator = WindowAggregator()
    extractor = FeatureExtractor()

    scores = []

    for pkt in packets:
        packet_dict = scapy_to_packet_dict(pkt)
        if packet_dict is None:
            continue

        # Update flow tracker with normalized packet
        flow_tracker.update_flow(packet_dict)

        # Process any completed flows into windows
        windows = aggregator.add_flows(flow_tracker.get_completed_flows())
        if not windows:
            continue

        for window in windows:
            features = extractor.extract(window)
            if not features:
                continue

            X = [vectorize(features)]
            score = model.score(X)[0]
            scores.append(score)

    # ------------------------------------------------------------------
    # FINAL FLUSH: expire remaining flows after PCAP replay
    # ------------------------------------------------------------------
    final_flows = flush_active_flows(flow_tracker)
    windows = aggregator.add_flows(final_flows)

    if windows:
        for window in windows:
            features = extractor.extract(window)
            if not features:
                continue

            X = [vectorize(features)]
            score = model.score(X)[0]
            scores.append(score)

    return np.array(scores)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("[*] Loading Isolation Forest model...")
    model = IsolationForestModel()

    print("[*] Evaluating normal traffic...")
    normal_scores = evaluate_pcap("normal.pcap", model)

    print("[*] Evaluating anomalous traffic...")
    anomalous_scores = evaluate_pcap("anomalous.pcap", model)

    print("\n=== Evaluation Results ===")

    print("Normal PCAP:")
    if len(normal_scores) > 0:
        print(f"  Mean score: {normal_scores.mean():.4f}")
        print(f"  Std dev:    {normal_scores.std():.4f}")
    else:
        print("  No scores produced")

    print("\nAnomalous PCAP:")
    if len(anomalous_scores) > 0:
        print(f"  Mean score: {anomalous_scores.mean():.4f}")
        print(f"  Std dev:    {anomalous_scores.std():.4f}")
    else:
        print("  No scores produced")
