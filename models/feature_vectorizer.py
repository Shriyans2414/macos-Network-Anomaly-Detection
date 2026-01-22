# models/feature_vectorizer.py

FEATURE_ORDER = [
    "active_connections",
    "mean_packets_per_flow",
    "mean_bytes_per_flow",
    "avg_flow_duration",
    "max_flow_duration",
    "unique_dst_ip_count",
    "unique_dst_port_count",
    "dst_ip_entropy",
    "dst_port_entropy",
    "mean_inter_arrival",
    "std_inter_arrival"
]

def vectorize(features: dict):
    return [features.get(k, 0) for k in FEATURE_ORDER]
