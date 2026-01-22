"""
Baseline feature computation for explainability.

This represents normal traffic behavior.
"""

from scapy.all import rdpcap
from capture.flow_tracker import FlowTracker
from features.feature_extractor import FeatureExtractor


def compute_baseline_features(pcap_path="normal.pcap"):
    packets = rdpcap(pcap_path)
    flow_tracker = FlowTracker()

    for pkt in packets:
        if not pkt.haslayer("IP"):
            continue

        packet = {
            "src_ip": pkt["IP"].src,
            "dst_ip": pkt["IP"].dst,
            "src_port": pkt.sport if hasattr(pkt, "sport") else 0,
            "dst_port": pkt.dport if hasattr(pkt, "dport") else 0,
            "protocol": pkt.proto,
            "timestamp": float(pkt.time),
            "size": len(pkt)
        }

        flow_tracker.update_flow(packet)

    flows = flow_tracker.get_completed_flows() + flow_tracker.get_active_flows()
    extractor = FeatureExtractor()
    return extractor.extract(flows)
