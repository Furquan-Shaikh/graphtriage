"""
GraphTriage — Combined Explanation Module (Day 6, Step 3)

Merges FeatureExplainer (Step 1, SHAP keywords) and SimilarityExplainer
(Step 2, graph-based similar tickets) into one clean explanation object,
matching the output shape sketched in docs/design.md Section 3.3.

IMPORTANT: this module's "predicted_category" comes from the baseline
classifier (via FeatureExplainer), NOT the Day 5 GNN. This is a deliberate,
documented simplification (see docs/memory.md, Sprint Day 6 decision log) —
SHAP applies cleanly to the baseline's bag-of-words features but not to the
GNN's message-passing node features. As a consequence, /predict (GNN-based)
and /explain (baseline-based) can occasionally disagree on the predicted
category for the same ticket. That disagreement is real, useful signal —
it should be surfaced, not hidden. The similar-past-tickets' categories
returned here are their ACTUAL historical categories; they are never
rewritten to artificially match the prediction.
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
        predicted_category = feature_result["predicted_category"]

        if ticket_id is not None:
            similarity_result = self.similarity_explainer.explain_by_ticket_id(ticket_id)
        elif embedding is not None:
            similarity_result = self.similarity_explainer.explain_by_embedding(embedding)
        else:
            raise ValueError("Must provide either ticket_id or embedding for the similarity explanation.")

        confidence = float(
            self.feature_explainer.classifier.predict_proba(
                self.feature_explainer.vectorizer.transform([text])
            ).max()
        )

        return {
            "predicted_category": predicted_category,
            "top_contributing_features": [
                f"{f['feature']} ({f['contribution']:+.3f})"
                for f in feature_result["top_contributing_features"]
            ],
            "top_similar_past_tickets": [
                {
                    "ticket_id": n["ticket_id"],
                    "category": n["category"],  # real historical category - never overridden
                    "resolution_time_hours": n["resolution_time_hours"],
                    "similarity": n["similarity"],
                }
                for n in similarity_result["similar_past_tickets"]
            ],
            "confidence": round(confidence, 4),
        }

    @classmethod
    def load(cls, feature_path, similarity_path):
        feature_explainer = FeatureExplainer.load(feature_path)
        similarity_explainer = SimilarityExplainer.load(similarity_path)
        return cls(feature_explainer, similarity_explainer)
