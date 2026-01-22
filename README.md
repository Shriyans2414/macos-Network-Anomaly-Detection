# 🚦 Network Anomaly Detection System (macOS)
A real-time, host-based network anomaly detection system that monitors live network traffic, learns normal behavior using unsupervised machine learning, and flags abnormal activity in real time with a live dashboard.

This project is designed as a **lightweight endpoint agent + central monitoring service**, similar in spirit to enterprise intrusion detection and EDR systems.

---
## 🔍 What This Project Does
- Captures live network traffic on macOS
- Groups packets into flow-level conversations
- Extracts behavioral features over sliding time windows
- Learns normal network behavior using an Isolation Forest (unsupervised)
- Detects and scores anomalous behavior in real time
- Exposes results via a FastAPI endpoint
- Displays live status on a Streamlit dashboard

The system **does not inspect payloads** and operates only on network metadata, making it privacy-safe and efficient.

---
## 🧠 System Architecture
Host (Agent)
├── Packet Capture (Scapy)
├── Flow Aggregation
├── Sliding Window Feature Extraction
└── Feature Transmission
↓
Central Service
├── Isolation Forest (Training + Inference)
├── Anomaly Scoring
├── Severity Classification
├── FastAPI (/status)
└── Streamlit Dashboard

## Architecture Diagram
                ┌──────────────────────────┐
                │     Network Interface    │
                │   (macOS en0 / lo0 etc.) │
                └────────────┬─────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│                  Packet Capture Layer                  │
│                  (Scapy Sniffer)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ capture/packet_sniffer.py                        │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 ▼                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ capture/flow_tracker.py                          │  │
│  │ • Flow keying (src/dst/proto/ports)              │  │
│  │ • Packet & byte counts                           │  │
│  │ • Flow expiration                                │  │
│  └──────────────┬───────────────────────────────────┘  │
└─────────────────┼──────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│               Feature Engineering Layer                │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ features/window_aggregator.py                    │  │
│  │ • Time-window batching                           │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 ▼                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ features/feature_extractor.py                    │  │
│  │ • Flow statistics                                │  │
│  │ • Rate & volume features                         │  │
│  └──────────────┬───────────────────────────────────┘  │
└─────────────────┼──────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│            Machine Learning Detection Layer            │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ models/vectorizer.py                             │  │
│  │ • Numeric feature vector                         │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 ▼                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ models/isolation_forest.py                       │  │
│  │ • Unsupervised anomaly detection                 │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 ▼                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ models/severity.py                               │  │
│  │ • Score → severity mapping                       │  │
│  └──────────────┬───────────────────────────────────┘  │
└─────────────────┼──────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│               State & Access Layer                     │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ storage/state.py                                 │  │
│  │ • In-memory anomaly state                        │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 ▼                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ api/server.py (FastAPI)                          │  │
│  │ • REST endpoints                                 │  │
│  └──────────────┬───────────────────────────────────┘  │
└─────────────────┼──────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│                 Visualization Layer                    │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ dashboard/dashboard.py (Streamlit)               │  │
│  │ • Real-time anomaly visualization                │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘

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

5. **API & Visualization**
   - FastAPI exposes anomaly data
   - Streamlit dashboard provides real-time visibility

This modular design allows each component (capture, features, model, UI) to be independently extended or replaced.

## 🔄 Data Flow
Network packets
   ↓
packet_sniffer.py
   ↓
flow_tracker.py
   ↓
window_aggregator.py
   ↓
feature_extractor.py
   ↓
ML model (Isolation Forest)
   ↓
anomaly score
   ↓
API + Dashboard

> Current implementation runs on a single machine for simplicity, but the design directly generalizes to multi-host organizational deployments.

---
## 🧪 Threat Model (What It Can Detect)
This system focuses on **behavioral anomalies**, not signature-based attacks.

Examples of detectable patterns:
- Sudden spikes in active connections
- Abnormally high destination IP or port fan-out
- Burst traffic inconsistent with baseline behavior
- Beaconing-like periodic traffic
- Potential data exfiltration patterns (metadata-level)

It is especially effective for **unknown or zero-day behaviors**.

---
## 🚨 Example Anomaly (Observed)
During stress testing with burst traffic:

🚨 ANOMALY DETECTED 🚨
Anomaly Score: -0.0478
active_connections: 89
unique_dst_ip_count: 25
unique_dst_port_count: 46
dst_ip_entropy: 3.04
dst_port_entropy: 4.49

Normal browsing traffic consistently produced positive anomaly scores.

---
## 📊 Evaluation (PCAP Replay)
- Normal traffic PCAPs consistently produced positive anomaly scores, while burst traffic PCAPs resulted in negative scores and HIGH severity alerts.
- Since the model is unsupervised, evaluation focuses on behavioral separation rather than labeled accuracy metrics.

| Traffic Type | Avg Anomaly Score |  Result |
|--------------|-------------------|---------|
| Normal PCAP  |  +0.05 to +0.10   |  NORMAL |
| Burst PCAP   |  -0.03 to -0.10   | ANOMALY |

---
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

---
## 🚦 Dashboard States
- **TRAINING**  
  Model is learning baseline behavior from normal traffic.
- **NORMAL**  
  Current network behavior matches learned baseline.
- **ANOMALY**  
  Network behavior deviates significantly from baseline.

---
## ▶️ How to Run
0️⃣ Install Requirements
pip install -r requirements.txt

1️⃣ Packet Sniffer + ML Engine
sudo python3 -m capture.packet_sniffer

2️⃣ API Server
python3 -m uvicorn api.server:app

3️⃣ Dashboard
streamlit run dashboard/dashboard.py

4️⃣ Offline Evaluation
python evaluation/evaluate_pcap.py

---
## 🧪 Generating Test Traffic
- Normal traffic:
ping google.com
curl https://example.com

- Anomalous traffic:
for i in {1..20}; do curl https://example.com & done

---
## ⚠️ Limitations
- Host-based visibility only
- No encrypted payload inspection
- No long-term concept drift handling yet
- File-based IPC (chosen for simplicity and reliability)
- These trade-offs were intentional to keep the system  lightweight and explainable.

---
## Future Enhancements
- Multi-host agent ingestion
- Historical anomaly score visualization

---
## 🎯 Why This Project Matters
This project demonstrates:
- Systems & networking fundamentals
- Real-time data pipelines
- Appropriate use of unsupervised ML
- Production-aware software design
- Debugging real-world OS and process issues
- It is representative of how real anomaly detection systems are built—at a smaller, explainable scale.