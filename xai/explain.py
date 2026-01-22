"""
Explainability module for Network Anomaly Detection

Provides feature-level explanations by comparing
current feature values against a baseline.
"""

import numpy as np

class AnomalyExplainer:
    def __init__(self, feature_names):
        self.feature_names = feature_names

    def explain(self, baseline_features, current_features, top_k=5):
        """
        Compare current features to baseline and return
        top contributing features.

        baseline_features: dict
        current_features: dict
        """

        explanations = []

        for name in self.feature_names:
            base_val = baseline_features.get(name, 0)
            curr_val = current_features.get(name, 0)

            delta = abs(curr_val - base_val)
            explanations.append((name, delta, curr_val, base_val))

        # Sort by contribution
        explanations.sort(key=lambda x: x[1], reverse=True)

        return explanations[:top_k]
