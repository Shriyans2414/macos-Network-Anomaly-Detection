# models/isolation_forest.py

import os
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

MODEL_PATH = "models/isolation_forest.pkl"

class IsolationForestModel:
    def __init__(self, contamination=0.05):
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42
        )
        self.is_trained = False

    def fit(self, X):
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True

    def score(self, x):
        if not self.is_trained:
            return None, None

        x_scaled = self.scaler.transform([x])
        score = self.model.decision_function(x_scaled)[0]
        label = self.model.predict(x_scaled)[0]  # -1 = anomaly
        return score, label

    def save(self):
        joblib.dump(
            {
                "model": self.model,
                "scaler": self.scaler
            },
            MODEL_PATH
        )

    def load(self):
        if not os.path.exists(MODEL_PATH):
            return False

        data = joblib.load(MODEL_PATH)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.is_trained = True
        return True
