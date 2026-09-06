"""
GraphTriage — SHAP Feature-Level Explainer (Day 6, Step 1)

Wraps the Day 4 baseline (TF-IDF + Logistic Regression) as a reusable
explainability component: fit once on training data, then explain any
ticket's predicted category by its top contributing words/phrases.

Why the baseline model for explanations, not the GNN directly: SHAP is
designed for models with a well-defined per-feature input (like TF-IDF's
bag-of-words vector), not for graph-structured models where "features" of
a node are entangled with its neighbors' features through message passing.
Using the baseline here is a deliberate, documented simplification for the
lightweight sprint (see docs/memory.md decision log) — it still gives a
genuine, correct explanation of which *words* matter, while the graph-based
"similar tickets" explanation (Step 2) covers the structural/relational
side that SHAP can't.

Usage as a module (Day 7 onward, live serving):
    explainer = FeatureExplainer()
    explainer.fit(train_texts, train_labels)
    explainer.save("feature_explainer.joblib")
    ...
    explainer = FeatureExplainer.load("feature_explainer.joblib")
    result = explainer.explain("Payment service timing out under load. ...")
"""

import joblib
import numpy as np
import shap
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


class FeatureExplainer:
    def __init__(self, max_features=5000, top_k=5):
        self.vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2), stop_words="english")
        self.classifier = LogisticRegression(max_iter=1000, random_state=42)
        self.explainer = None
        self.top_k = top_k

    def fit(self, texts, labels):
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        # Keep a background sample for SHAP (and for reconstructing the
        # explainer after save/load, since the explainer object itself
        # isn't easily picklable).
        self._background = X[:200]
        self.explainer = shap.LinearExplainer(self.classifier, self._background)
        return self

    def explain(self, text):
        """Returns the predicted category plus its top contributing words/phrases."""
        X = self.vectorizer.transform([text])
        predicted_class = self.classifier.predict(X)[0]
        class_idx = list(self.classifier.classes_).index(predicted_class)

        shap_values = self.explainer(X)
        # shape: (1, n_features, n_classes) -> take our one sample, our predicted class
        contributions = shap_values.values[0, :, class_idx]

        feature_names = np.array(self.vectorizer.get_feature_names_out())
        top_indices = np.argsort(np.abs(contributions))[-self.top_k:][::-1]

        top_features = [
            {"feature": feature_names[i], "contribution": round(float(contributions[i]), 4)}
            for i in top_indices
            if contributions[i] != 0
        ]

        return {
            "predicted_category": predicted_class,
            "top_contributing_features": top_features,
        }

    def save(self, path):
        joblib.dump(
            {
                "vectorizer": self.vectorizer,
                "classifier": self.classifier,
                "background": self._background,
                "top_k": self.top_k,
            },
            path,
        )

    @classmethod
    def load(cls, path):
        state = joblib.load(path)
        instance = cls(top_k=state["top_k"])
        instance.vectorizer = state["vectorizer"]
        instance.classifier = state["classifier"]
        instance._background = state["background"]
        instance.explainer = shap.LinearExplainer(instance.classifier, instance._background)
        return instance
