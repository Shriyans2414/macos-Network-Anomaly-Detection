from scapy.all import sniff, IP, TCP, UDP, ICMP
import time
from datetime import datetime

from capture.flow_tracker import FlowTracker
from features.window_aggregator import WindowAggregator
from features.feature_extractor import FeatureExtractor
from models.isolation_forest import IsolationForestModel
from models.feature_vectorizer import vectorize
from models.severity import classify_severity
from storage.state import write_state

from xai.explain import AnomalyExplainer
from xai.baseline import compute_baseline_features


# =====================
# CONFIGURATION
# =====================
FLOW_TIMEOUT = 60           # seconds
WINDOW_SIZE = 30            # seconds
FEATURE_INTERVAL = 10       # seconds
TRAINING_SAMPLES = 30       # number of windows for baseline


# =====================
# INITIALIZE COMPONENTS
# =====================
tracker = FlowTracker(flow_timeout=FLOW_TIMEOUT)
window_agg = WindowAggregator(window_size=WINDOW_SIZE)
feature_extractor = FeatureExtractor()
model = IsolationForestModel(contamination=0.05)

training_buffer = []

# Load model if present
if model.load():
    print("[MODEL LOADED] Using saved baseline model")

LAST_FEATURE_TIME = time.time()

# ---------------------
# Explainability (ONE-TIME INIT)
# ---------------------
baseline_features = compute_baseline_features()

explainer = AnomalyExplainer(
    feature_names=list(baseline_features.keys())
)


# =====================
# PACKET PROCESSING
# =====================
def process_packet(packet):
    global LAST_FEATURE_TIME

    try:
        # Only process IP packets
        if IP not in packet:
            return

        ip_layer = packet[IP]
        proto = "OTHER"
        src_port = 0
        dst_port = 0

        if TCP in packet:
            proto = "TCP"
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
        elif UDP in packet:
            proto = "UDP"
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
        elif ICMP in packet:
            proto = "ICMP"

        packet_data = {
            "src_ip": ip_layer.src,
            "dst_ip": ip_layer.dst,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": proto,
            "size": len(packet),
            "timestamp": time.time()
        }

        # ---------------------
        # Flow tracking
        # ---------------------
        tracker.update_flow(packet_data)

        # ---------------------
        # Periodic feature extraction
        # ---------------------
        now = time.time()
        if now - LAST_FEATURE_TIME < FEATURE_INTERVAL:
            return

        LAST_FEATURE_TIME = now

        active_flows = tracker.get_active_flows()
        if not active_flows:
            return

        window_agg.add_flows(active_flows)
        window = window_agg.get_window()

        features = feature_extractor.extract(window)
        if not features:
            return

        x = vectorize(features)

        # ---------------------
        # TRAINING PHASE
        # ---------------------
        if not model.is_trained:
            training_buffer.append(x)
            print(f"[TRAINING] collected {len(training_buffer)} / {TRAINING_SAMPLES}")

            write_state({
                "status": "TRAINING",
                "severity": "UNKNOWN",
                "score": None,
                "features": features,
                "explanations": []
            })

            if len(training_buffer) >= TRAINING_SAMPLES:
                model.fit(training_buffer)
                model.save()
                print("\n[MODEL TRAINED & SAVED] Isolation Forest baseline learned\n")
            return

        # ---------------------
        # DETECTION PHASE
        # ---------------------
        score, label = model.score(x)
        severity = classify_severity(score)

        explanations = []

        if label == -1:
            raw_explanations = explainer.explain(
                baseline_features,
                features
            )

            explanations = [
                {
                    "feature": name,
                    "deviation": deviation,
                    "current": current,
                    "baseline": baseline
                }
                for name, deviation, current, baseline in raw_explanations
            ]

            write_state({
                "status": "ANOMALY",
                "severity": severity,
                "score": float(score),
                "features": features,
                "explanations": explanations
            })

            print("\n🚨 ANOMALY DETECTED 🚨")
            print(f"Anomaly Score: {score:.4f}")
            for k, v in features.items():
                print(f"{k}: {v}")

        else:
            write_state({
                "status": "NORMAL",
                "severity": "NONE",
                "score": float(score),
                "features": features,
                "explanations": []
            })

            print(f"[NORMAL] score={score:.4f}")

    except Exception as e:
        print(f"[ERROR] {e}")


# =====================
# START SNIFFING
# =====================
def start_sniffing():
    print("[*] Starting packet capture with ML-based anomaly detection...")
    sniff(prn=process_packet, store=False)


if __name__ == "__main__":
    start_sniffing()
