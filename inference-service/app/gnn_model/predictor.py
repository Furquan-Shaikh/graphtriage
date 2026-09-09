"""
GraphTriage — Inductive GNN Predictor for New Tickets (Day 7, Step 1)

Day 5's GNN was trained transductively on the full fixed graph of 1200
existing tickets. To predict for a BRAND-NEW ticket (not in that graph),
this module uses GraphSAGE's inductive capability: build a small subgraph
connecting the new ticket to its k-nearest-neighbor existing tickets (by
embedding similarity), then run the trained model's forward pass on that
subgraph — SAGEConv works on any graph structure, not just the one it was
trained on, as long as node features are in the same space.

Usage:
    predictor = GNNPredictor.load(
        model_path=".../gnn_model.pt",
        graph_dataset_path=".../graph_dataset.pt",
    )
    result = predictor.predict(text="Payment service timing out under load...")
"""

import torch
from sklearn.neighbors import NearestNeighbors

from app.embeddings.embedder import embed_texts
from app.gnn_model.model import GraphTriageGNN


class GNNPredictor:
    def __init__(self, model, existing_embeddings, category_classes, k=5, hidden_channels=64):
        self.model = model
        self.existing_embeddings = existing_embeddings  # (N, dim) tensor, the original training nodes
        self.category_classes = category_classes
        self.k = k
        self.nn = NearestNeighbors(n_neighbors=k, metric="cosine").fit(existing_embeddings.numpy())

    def predict(self, text):
        # 1. Embed the new ticket
        new_embedding = embed_texts([text])[0]  # numpy array, shape (dim,)
        new_embedding_t = torch.tensor(new_embedding, dtype=torch.float)

        # 2. Find its k nearest existing tickets
        _, neighbor_indices = self.nn.kneighbors(new_embedding.reshape(1, -1))
        neighbor_indices = neighbor_indices[0]  # shape (k,)

        # 3. Build a small subgraph: node 0 = new ticket, nodes 1..k = its neighbors
        neighbor_features = self.existing_embeddings[neighbor_indices]  # (k, dim)
        x = torch.cat([new_embedding_t.unsqueeze(0), neighbor_features], dim=0)  # (k+1, dim)

        # Connect the new node (index 0) bidirectionally to each neighbor (indices 1..k)
        edges = []
        for i in range(1, len(x)):
            edges.append((0, i))
            edges.append((i, 0))
        edge_index = torch.tensor(edges, dtype=torch.long).T

        # 4. Forward pass on this subgraph
        self.model.eval()
        with torch.no_grad():
            category_logits, resolution_pred = self.model(x, edge_index)

        # Extract predictions for node 0 (the new ticket)
        probs = torch.softmax(category_logits[0], dim=0)
        predicted_idx = int(torch.argmax(probs))
        predicted_category = self.category_classes[predicted_idx]
        confidence = float(probs[predicted_idx])
        predicted_resolution_hours = float(resolution_pred[0])

        return {
            "predicted_category": predicted_category,
            "predicted_resolution_hours": round(predicted_resolution_hours, 2),
            "confidence": round(confidence, 4),
        }, new_embedding

    @classmethod
    def load(cls, model_path, graph_dataset_path, k=5):
        checkpoint = torch.load(model_path, weights_only=False)
        graph_data = torch.load(graph_dataset_path, weights_only=False)

        category_classes = checkpoint["category_classes"]
        model = GraphTriageGNN(
            in_channels=graph_data["x"].shape[1],
            hidden_channels=64,  # must match the hidden size used in train_gnn.py
            num_categories=len(category_classes),
        )
        model.load_state_dict(checkpoint["model_state_dict"])

        return cls(
            model=model,
            existing_embeddings=graph_data["x"],
            category_classes=category_classes,
            k=k,
        )
