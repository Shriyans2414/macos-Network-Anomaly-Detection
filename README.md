## 🚦 Explainable Network Anomaly Detection System (macOS)

A real-time, host-based network anomaly detection system for macOS that monitors live network traffic, learns normal behavior using unsupervised machine learning, and flags anomalous activity with human-readable explanations, exposed via an API and a live dashboard.

This project is designed as a **lightweight endpoint agent + monitoring service**, inspired by enterprise IDS / EDR systems, but built to be **explainable, privacy-preserving, and reproducible**.

## What This System Does
At a high level, the system:
- Captures live network traffic on macOS
- Groups packets into flow-level conversations
- Extracts behavioral features over sliding time windows
- Learns baseline behavior using Isolation Forest
- Detects anomalous network behavior in real time
- Assigns severity levels to anomalies
- Explains why an anomaly was flagged
- Exposes results via a FastAPI backend
- Visualizes status and explanations in a Streamlit dashboard

**Payloads are never inspected**.
The system operates purely on network metadata, making it privacy-safe and efficient.

## Key Design Principles
- Explainability over black-box accuracy
- Behavioral detection, not signatures
- Modular architecture (capture, features, ML, API, UI)
- Offline reproducibility + online inference
- Production-aware engineering choices

## System Architecture
Network Interface (macOS)
        ↓
Packet Capture (Scapy)
        ↓
Flow Tracking
        ↓
Windowed Feature Extraction
        ↓
Unsupervised ML (Isolation Forest)
        ↓
Severity Classification
        ↓
Explainability Layer
        ↓
FastAPI Backend (/status)
        ↓
Streamlit Dashboard

## Architecture Overview
- This system implements a flow-based, real-time network anomaly detection pipeline for macOS.
- The architecture is divided into clearly separated layers:

1. **Packet Capture**
   - Live packet sniffing using Scapy
   - Protocol-aware parsing (TCP, UDP, ICMP)

2. **Flow Tracking**
   - Packets are grouped into flows
   - Flow expiration prevents memory growth

3. **Feature Engineering**
   - Flows are aggregated in fixed time windows
   - Statistical features are extracted for ML

4. **Machine Learning**
   - Unsupervised anomaly detection using Isolation Forest
   - Severity mapping for interpretability
   - Trained on normal traffic only
   - Produces anomaly scores (lower = more anomalous)
   - Designed for unknown / zero-day behaviors

5. **Severity Classification**
   - Raw anomaly scores are mapped to: Low,Medium,High
   - This makes alerts actionable, not just numeric.

6. **Explainability Layer**
When an anomaly is detected, the system:
   - When an anomaly is detected, the system:
   - Ranks features by deviation
   - Produces human-readable explanations, e.g.:
“Destination IP entropy increased significantly compared to baseline.”

7. **API & State Management**
   - FastAPI backend exposes system state via /status
   - Detection results + explanations are persisted in a shared state store
   - Enables decoupling between detection and visualization

8. **Dashboard (Streamlit)**
The dashboard provides:
   - Live system status
   - Severity indicators
   - Feature snapshots
   - “Why was this flagged?” explanations
This mirrors how real SOC tools present alerts.

## Data Flow
Packets
   - packet_sniffer.py
   - flow_tracker.py
   - window_aggregator.py
   - feature_extractor.py
   - Isolation Forest
   - severity mapping
   - explainability
   - API
   - dashboard

The current implementation runs on a single host for simplicity, but the design naturally extends to multi-host deployments.

## Threat Model (What It Can Detect)
This system focuses on **behavioral anomalies**, not signature-based attacks.

Examples of detectable patterns:
- Sudden spikes in active connections
- Abnormally high destination IP or port fan-out
- Burst traffic inconsistent with baseline behavior
- Beaconing-like periodic traffic
- Potential data exfiltration patterns (metadata-level)

It is especially effective for **unknown or zero-day behaviors**.

## Example Anomaly (Observed)
During burst-traffic testing:
Status: ANOMALY
Severity: LOW
Anomaly Score: -0.0133

active_connections: 37
unique_dst_ip_count: 16
unique_dst_port_count: 18
dst_ip_entropy: 3.13
dst_port_entropy: 3.29
inter_arrival_std: 9.02

Normal browsing traffic consistently produced positive anomaly scores.

## Evaluation (PCAP Replay)
- Normal traffic PCAPs consistently produced positive anomaly scores, while burst traffic PCAPs resulted in negative scores and HIGH severity alerts.
- Since the model is unsupervised, evaluation focuses on behavioral separation rather than labeled accuracy metrics.

| Traffic Type | Avg Anomaly Score |  Result |
|--------------|-------------------|---------|
| Normal PCAP  |  +0.05 to +0.10   |  NORMAL |
| Burst PCAP   |  -0.03 to -0.10   | ANOMALY |

Evaluation focuses on behavioral separation, not labeled accuracy, which is appropriate for unsupervised detection.

## Offline Evaluation
The project includes an offline evaluation script (`evaluation/evaluate_pcap.py`)
to validate the anomaly detection pipeline using recorded network traffic.

The evaluation script replays PCAP files through the same pipeline used for live
traffic:
- Packet parsing
- Flow reconstruction
- Time-window aggregation
- Feature extraction
- Anomaly scoring using Isolation Forest

This allows reproducible testing without requiring live packet capture.

## 🚦 Dashboard States
- **TRAINING**  
  Model is learning baseline behavior from normal traffic.
- **NORMAL**  
  Current network behavior matches learned baseline.
- **ANOMALY**  
  Network behavior deviates significantly from baseline.

## ▶️ How to Run
0️⃣ Install Requirements

pip install -r requirements.txt

1️⃣ Packet Sniffer + ML Engine

sudo python -m capture.packet_sniffer

2️⃣ API Server

python run.py

3️⃣ Dashboard

streamlit run dashboard/dashboard.py

4️⃣ Offline Evaluation

python evaluation/evaluate_pcap.py

## Generating Test Traffic
- Normal traffic:

ping google.com
curl https://example.com

- Anomalous traffic:

for i in {1..20}; do curl https://example.com & done

## Limitations(Intentional)
- Host-based visibility only
- No encrypted payload inspection
- No long-term concept drift handling yet
- File-based IPC (chosen for simplicity and reliability).
These trade-offs were intentional to keep the system lightweight and explainable.

## Future Enhancements
- Multi-host agent ingestion
- Historical anomaly score visualization
- Online / adaptive learning
- Streaming backend (Kafka / Redis)

## Why This Project Matters
This project demonstrates:
- Strong networking and systems fundamentals
- Real-time data pipelines
- Appropriate use of unsupervised ML
- Explainability in security ML
- API + dashboard integration
- Production-aware engineering decisions
This is representative of how real anomaly detection systems are built, at a smaller, explainable, and inspectable scale.