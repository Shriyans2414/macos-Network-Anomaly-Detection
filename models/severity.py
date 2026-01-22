# models/severity.py

def classify_severity(score: float):
    """
    Lower score = more anomalous
    Thresholds chosen empirically for Isolation Forest
    """
    if score is None:
        return "UNKNOWN"

    if score < -0.10:
        return "HIGH"
    elif score < -0.03:
        return "MEDIUM"
    else:
        return "LOW"
