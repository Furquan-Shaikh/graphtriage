"""
GraphTriage — Combined Explanation Module (Day 6, Step 3)

Merges FeatureExplainer (Step 1, SHAP keywords) and SimilarityExplainer
(Step 2, graph-based similar tickets) into one clean explanation object,
matching the output shape sketched in docs/design.md Section 3.3:

{
  "top_contributing_features": [...],
  "top_similar_past_tickets": [...],
  "confidence": 0.83
}

This is the module the live API (Day 7 onward) will call for the
`/explain` endpoint.

Usage:
    explainer = CombinedExplainer.load(
        feature_path="feature_explainer.joblib",
        similarity_path="similarity_explainer.joblib",
    )
    result = explainer.explain(text="...", ticket_id=482)          # existing ticket
    result = explainer.explain(text="...", embedding=some_vector)  # brand-new ticket
"""

from app.explainability.feature_explainer import FeatureExplainer
from app.explainability.similarity_explainer import SimilarityExplainer


class CombinedExplainer:
    def __init__(self, feature_explainer: FeatureExplainer, similarity_explainer: SimilarityExplainer):
        self.feature_explainer = feature_explainer
        self.similarity_explainer = similarity_explainer

    def explain(self, text, ticket_id=None, embedding=None):
        """
        text: the ticket's title + description text (for SHAP keyword explanation)
        ticket_id: if this is an existing ticket already in the fitted data
        embedding: if this is a brand-new ticket, its precomputed embedding
                   (required if ticket_id is not provided)
        """
        feature_result = self.feature_explainer.explain(text)

        if ticket_id is not None:
            similarity_result = self.similarity_explainer.explain_by_ticket_id(ticket_id)
        elif embedding is not None:
            similarity_result = self.similarity_explainer.explain_by_embedding(embedding)
        else:
            raise ValueError("Must provide either ticket_id or embedding for the similarity explanation.")

        # Estimate a simple confidence score from the classifier's own probability
        # for its predicted class (a lightweight stand-in, not the GNN's confidence,
        # matching this module's baseline-model-based feature explanation approach).
        confidence = self.feature_explainer.classifier.predict_proba(
            self.feature_explainer.vectorizer.transform([text])
        ).max()

        return {
            "predicted_category": feature_result["predicted_category"],
            "top_contributing_features": [
                f"{f['feature']} ({f['contribution']:+.3f})"
                for f in feature_result["top_contributing_features"]
            ],
            "top_similar_past_tickets": [
                {
                    "ticket_id": n["ticket_id"],
                    "category": n["category"],
                    "resolution_time_hours": n["resolution_time_hours"],
                    "similarity": n["similarity"],
                }
                for n in similarity_result["similar_past_tickets"]
            ],
            "confidence": round(float(confidence), 4),
        }

    @classmethod
    def load(cls, feature_path, similarity_path):
        feature_explainer = FeatureExplainer.load(feature_path)
        similarity_explainer = SimilarityExplainer.load(similarity_path)
        return cls(feature_explainer, similarity_explainer)
