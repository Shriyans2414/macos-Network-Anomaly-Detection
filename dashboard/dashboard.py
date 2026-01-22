import streamlit as st
import requests
import time
from datetime import datetime

# =====================
# CONFIG
# =====================
STATUS_API_URL = "http://127.0.0.1:8000/status"
ANALYZE_API_URL = "http://127.0.0.1:8000/analyze"
REFRESH_INTERVAL = 3  # seconds


# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Network Anomaly Detection",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 Network Anomaly Detection Dashboard")
st.caption("Real-time host-based anomaly detection with explainable ML")

placeholder = st.empty()


# =====================
# HELPER FUNCTIONS
# =====================
def severity_color(severity):
    if severity == "HIGH":
        return "🔴 HIGH"
    elif severity == "MEDIUM":
        return "🟠 MEDIUM"
    elif severity == "LOW":
        return "🟡 LOW"
    elif severity == "NONE":
        return "🟢 NONE"
    return "⚪ UNKNOWN"


def render_explanations(explanations):
    st.subheader("🧠 Why was this flagged?")

    for exp in explanations:
        with st.expander(f"🔍 {exp['feature']}"):
            st.write(f"**Current value:** {round(exp['current'], 4)}")
            st.write(f"**Baseline value:** {round(exp['baseline'], 4)}")
            st.write(f"**Deviation:** {round(exp['deviation'], 4)}")


# =====================
# MAIN LOOP
# =====================
while True:
    try:
        # -------------------------
        # Fetch system status
        # -------------------------
        status_response = requests.get(STATUS_API_URL, timeout=2)
        status_data = status_response.json()

    except Exception:
        st.error("Unable to connect to API")
        time.sleep(REFRESH_INTERVAL)
        continue

    with placeholder.container():

        # -------- STATUS ROW --------
        col1, col2, col3 = st.columns(3)

        status = status_data.get("status", "UNKNOWN")
        severity = status_data.get("severity", "UNKNOWN")
        score = status_data.get("score", None)
        timestamp = status_data.get("timestamp", None)

        col1.metric("Status", status)
        col2.metric("Severity", severity_color(severity))
        col3.metric("Anomaly Score", f"{score:.4f}" if score is not None else "—")

        st.divider()

        # -------- TIME --------
        if timestamp:
            try:
                ts = datetime.fromisoformat(timestamp)
                st.caption(f"Last Updated: {ts.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception:
                st.caption(f"Last Updated: {timestamp}")
        else:
            st.caption("Last Updated: —")

        st.divider()

        # -------- ALERT BANNER --------
        if status == "ANOMALY":
            if severity == "HIGH":
                st.error("🚨 HIGH SEVERITY NETWORK ANOMALY DETECTED")
            elif severity == "MEDIUM":
                st.warning("⚠️ MEDIUM SEVERITY NETWORK ANOMALY DETECTED")
            else:
                st.info("ℹ️ LOW SEVERITY NETWORK ANOMALY DETECTED")
        elif status == "NORMAL":
            st.success("✅ Network behavior is normal")
        elif status == "TRAINING":
            st.info("🧠 Model is learning baseline network behavior")

        st.divider()

        # -------- FEATURE SNAPSHOT --------
        features = status_data.get("features", {})

        if features:
            st.subheader("📊 Feature Snapshot")

            fcol1, fcol2, fcol3 = st.columns(3)

            fcol1.metric("Active Connections", features.get("active_connections", 0))
            fcol1.metric("Unique Destination IPs", features.get("unique_dst_ip_count", 0))
            fcol1.metric("Unique Destination Ports", features.get("unique_dst_port_count", 0))

            fcol2.metric("Mean Packets / Flow", round(features.get("mean_packets_per_flow", 0), 2))
            fcol2.metric("Mean Bytes / Flow", round(features.get("mean_bytes_per_flow", 0), 2))
            fcol2.metric("Avg Flow Duration (s)", round(features.get("avg_flow_duration", 0), 2))

            fcol3.metric("Dst IP Entropy", round(features.get("dst_ip_entropy", 0), 3))
            fcol3.metric("Dst Port Entropy", round(features.get("dst_port_entropy", 0), 3))
            fcol3.metric("Inter-arrival Std", round(features.get("std_inter_arrival", 0), 3))
        else:
            st.info("No feature data available yet")

        st.divider()

        # -------- EXPLANATIONS --------
        explanations = status_data.get("explanations", [])

        if explanations:
            render_explanations(explanations)
        elif status == "ANOMALY":
            st.info("No explanations available for this anomaly yet")

    time.sleep(REFRESH_INTERVAL)
