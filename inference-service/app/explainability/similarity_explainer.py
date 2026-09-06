"""
GraphTriage — Similarity-Based Graph Explainer (Day 6, Step 2)

Given a ticket (existing or brand new), finds its top-K most similar past
tickets by embedding cosine similarity — this is the "graph-path"
explanation described in docs/design.md Section 3.1, adapted for a
GraphSAGE (not GAT) model: instead of attention weights, we surface the
actual neighbor tickets the GNN aggregates information from.

Works in two modes:
  - explain_by_ticket_id(): for a ticket already in the dataset (has a
    precomputed embedding)
  - explain_by_embedding(): for a brand-new ticket's embedding, computed
    on the fly (this is what Day 7's live API will call for incoming
    tickets it has never seen before)

Usage as a module:
    explainer = SimilarityExplainer()
    explainer.fit(ticket_ids, embeddings, categories, resolution_times)
    explainer.save("similarity_explainer.joblib")
    ...
    explainer = SimilarityExplainer.load("similarity_explainer.joblib")
    result = explainer.explain_by_ticket_id(482)
    result = explainer.explain_by_embedding(new_embedding)
"""

import joblib
import numpy as np
from sklearn.neighbors import NearestNeighbors


class SimilarityExplainer:
    def __init__(self, k=5):
        self.k = k
        self.nn = None
        self.ticket_ids = None
        self.embeddings = None
        self.categories = None
        self.resolution_times = None

    def fit(self, ticket_ids, embeddings, categories, resolution_times):
        """
        ticket_ids: array-like of ticket IDs, aligned with embeddings rows
        embeddings: (n, dim) array
        categories: dict {ticket_id: category}
        resolution_times: dict {ticket_id: resolution_time_hours}
        """
        self.ticket_ids = np.array(ticket_ids)
        self.embeddings = np.asarray(embeddings)
        self.categories = categories
        self.resolution_times = resolution_times
        self.nn = NearestNeighbors(n_neighbors=self.k + 1, metric="cosine").fit(self.embeddings)
        return self

    def _format_neighbors(self, distances, indices, exclude_ticket_id=None):
        results = []
        for dist, idx in zip(distances, indices):
            tid = int(self.ticket_ids[idx])
            if tid == exclude_ticket_id:
                continue
            results.append(
                {
                    "ticket_id": tid,
                    "category": self.categories.get(tid, "unknown"),
                    "resolution_time_hours": self.resolution_times.get(tid),
                    "similarity": round(1 - float(dist), 4),  # cosine distance -> similarity
                }
            )
            if len(results) == self.k:
                break
        return results

    def explain_by_ticket_id(self, ticket_id):
        """Explain a ticket that's already in the fitted dataset."""
        matches = np.where(self.ticket_ids == ticket_id)[0]
        if len(matches) == 0:
            raise ValueError(f"Ticket ID {ticket_id} not found in fitted data.")
        index = matches[0]

        distances, indices = self.nn.kneighbors(self.embeddings[index : index + 1])
        neighbors = self._format_neighbors(distances[0], indices[0], exclude_ticket_id=ticket_id)

        return {
            "ticket_id": ticket_id,
            "category": self.categories.get(ticket_id, "unknown"),
            "similar_past_tickets": neighbors,
        }

    def explain_by_embedding(self, embedding, new_ticket_label="new_ticket"):
        """Explain a brand-new ticket given its embedding (Day 7 live use case)."""
        embedding = np.asarray(embedding).reshape(1, -1)
        distances, indices = self.nn.kneighbors(embedding)
        neighbors = self._format_neighbors(distances[0], indices[0])

        return {
            "ticket_id": new_ticket_label,
            "similar_past_tickets": neighbors,
        }

    def save(self, path):
        joblib.dump(
            {
                "k": self.k,
                "ticket_ids": self.ticket_ids,
                "embeddings": self.embeddings,
                "categories": self.categories,
                "resolution_times": self.resolution_times,
            },
            path,
        )

    @classmethod
    def load(cls, path):
        state = joblib.load(path)
        instance = cls(k=state["k"])
        instance.fit(state["ticket_ids"], state["embeddings"], state["categories"], state["resolution_times"])
        return instance
