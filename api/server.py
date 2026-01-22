from fastapi import FastAPI
import joblib
import numpy as np

from storage.state import read_state
from features.feature_extractor import FeatureExtractor
from models.severity import classify_severity

from xai.explain import AnomalyExplainer
from xai.baseline import compute_baseline_features


# --------------------------------------------------
# App initialization
# --------------------------------------------------
app = FastAPI(title="Network Anomaly Detection API")


# --------------------------------------------------
# Load trained model (offline-trained)
# --------------------------------------------------
model = joblib.load("models/isolation_forest.pkl")


# --------------------------------------------------
# Load baseline features ONCE at startup
# --------------------------------------------------
baseline_features = compute_baseline_features()

explainer = AnomalyExplainer(
    feature_names=list(baseline_features.keys())
)

feature_extractor = FeatureExtractor()


# --------------------------------------------------
# Health & status endpoints
# --------------------------------------------------
@app.get("/")
def root():
    return {"status": "Network Anomaly Detection API running"}


@app.get("/status")
def get_status():
    return read_state()


# --------------------------------------------------
# Analyze endpoint (WITH EXPLANATIONS)
# --------------------------------------------------
@app.post("/analyze")
def analyze_traffic(flows: list[dict]):
    """
    Analyze a batch of flows and return:
    - anomaly decision
    - severity level
    - feature-level explanations
    """

    # -------------------------
    # Feature extraction
    # -------------------------
    current_features = feature_extractor.extract(flows)

    if not current_features:
        return {
            "anomaly": False,
            "severity": "LOW",
            "explanations": []
        }

    X = np.array([list(current_features.values())])

    # -------------------------
    # Model inference
    # -------------------------
    score = model.decision_function(X)[0]
    is_anomaly = score < 0

    severity = classify_severity(score)

    # -------------------------
    # Explainability
    # -------------------------
    explanations = []
    if is_anomaly:
        raw_explanations = explainer.explain(
            baseline_features,
            current_features
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

    # -------------------------
    # API response
    # -------------------------
    return {
        "anomaly": is_anomaly,
        "severity": severity,
        "explanations": explanations
    }
