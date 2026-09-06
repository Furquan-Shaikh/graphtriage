"""
GraphTriage — GNN Model Architecture (Day 5, Step 2)

A 2-layer GraphSAGE encoder shared by two prediction heads, per
architecture.md Section 6 (ML Pipeline Architecture):
  - Classification head: predicts root-cause category
  - Regression head: predicts resolution time (hours)

Both heads share the same learned node representations (multi-task
learning) — the intuition being that "what kind of problem is this" and
"how long will it take to fix" should draw on the same underlying signal
about the ticket and its similar-ticket neighborhood.

This module is used by both:
  - training/train_gnn.py (Day 5, offline training)
  - the live FastAPI app (from Day 7 onward, for serving predictions)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv


class GraphTriageGNN(nn.Module):
    def __init__(self, in_channels, hidden_channels, num_categories, dropout=0.3):
        super().__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.dropout = dropout

        self.category_head = nn.Linear(hidden_channels, num_categories)
        self.resolution_head = nn.Linear(hidden_channels, 1)

    def encode(self, x, edge_index):
        """Shared GraphSAGE encoder — produces one representation per node
        that both prediction heads read from."""
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        return x

    def forward(self, x, edge_index):
        node_embeddings = self.encode(x, edge_index)
        category_logits = self.category_head(node_embeddings)
        resolution_pred = self.resolution_head(node_embeddings).squeeze(-1)
        return category_logits, resolution_pred


if __name__ == "__main__":
    # Quick smoke test with random data - confirms shapes flow correctly
    # through the model before wiring up real training (Step 3).
    num_nodes, in_channels, hidden_channels, num_categories = 20, 384, 64, 13

    x = torch.randn(num_nodes, in_channels)
    edge_index = torch.randint(0, num_nodes, (2, 60))

    model = GraphTriageGNN(in_channels, hidden_channels, num_categories)
    category_logits, resolution_pred = model(x, edge_index)

    print(f"category_logits shape: {category_logits.shape} (expected: [{num_nodes}, {num_categories}])")
    print(f"resolution_pred shape: {resolution_pred.shape} (expected: [{num_nodes}])")
    assert category_logits.shape == (num_nodes, num_categories)
    assert resolution_pred.shape == (num_nodes,)
    print("Smoke test passed - shapes are correct.")
