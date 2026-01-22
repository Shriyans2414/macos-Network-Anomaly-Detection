"""
Offline training pipeline for Network Anomaly Detection

NOTE:
- WindowAggregator is designed for LIVE traffic
- For OFFLINE PCAP training, we treat the entire trace as one window
"""

from scapy.all import rdpcap
import numpy as np
import joblib

from capture.flow_tracker import FlowTracker
from features.feature_extractor import FeatureExtractor
from models.isolation_forest import IsolationForest


# -------------------------
# Configuration
# -------------------------
NORMAL_PCAP_PATH = "normal.pcap"
MODEL_OUTPUT_PATH = "models/isolation_forest.pkl"

CONTAMINATION = 0.02
RANDOM_STATE = 42


# -------------------------
# Load packets
# -------------------------
print("[+] Loading normal traffic PCAP")
packets = rdpcap(NORMAL_PCAP_PATH)


# -------------------------
# Build flows
# -------------------------
print("[+] Building flows from PCAP")

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

# Combine completed + active flows
flows = flow_tracker.get_completed_flows() + flow_tracker.get_active_flows()

if not flows:
    raise RuntimeError("No flows extracted from PCAP")


# -------------------------
# Feature extraction (single offline window)
# -------------------------
print("[+] Extracting features from offline window")

extractor = FeatureExtractor()
features = extractor.extract(flows)

if not features:
    raise RuntimeError("Feature extraction failed")

X = np.array([list(features.values())])
print(f"[+] Training data shape: {X.shape}")


# -------------------------
# Train Isolation Forest
# -------------------------
print("[+] Training Isolation Forest")

model = IsolationForest(
    n_estimators=300,
    contamination=CONTAMINATION,
    random_state=RANDOM_STATE
)
model.fit(X)


# -------------------------
# Save model (local only)
# -------------------------
joblib.dump(model, MODEL_OUTPUT_PATH)
print(f"[✓] Model trained and saved to {MODEL_OUTPUT_PATH}")
