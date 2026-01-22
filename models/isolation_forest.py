import joblib
from sklearn.ensemble import IsolationForest
import os


class IsolationForestModel:
    def __init__(self, contamination=0.05, model_path="models/isolation_forest.pkl"):
        self.contamination = contamination
        self.model_path = model_path
        self.model = None
        self.is_trained = False

    def fit(self, X):
        self.model = IsolationForest(
            n_estimators=300,
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X)
        self.is_trained = True

    def score(self, x):
        """
        Returns (score, label)
        label = -1 → anomaly
        label = 1  → normal
        """
        score = self.model.decision_function([x])[0]
        label = self.model.predict([x])[0]
        return score, label

    def save(self):
        if self.model is None:
            raise RuntimeError("Cannot save untrained model")
        joblib.dump(self.model, self.model_path)

    def load(self):
        if not os.path.exists(self.model_path):
            return False

        self.model = joblib.load(self.model_path)
        self.is_trained = True
        return True
