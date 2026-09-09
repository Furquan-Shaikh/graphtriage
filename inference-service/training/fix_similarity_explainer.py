 
"""
Fix the similarity explainer with correct category mapping
"""
import os
import sys
import numpy as np
import mysql.connector
import joblib
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def load_env():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(repo_root, ".env"))

def get_mysql_connection():
    return mysql.connector.connect(
        host='localhost',
        port=3307,
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )

def main():
    load_env()
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    # Fetch all ticket categories and resolution times
    cursor.execute("""
        SELECT t.id, b.category, f.resolution_time_hours
        FROM ticket t
        JOIN bug b ON t.id = b.ticket_id
        JOIN fix f ON b.id = f.bug_id
    """)
    
    categories = {}
    resolution_times = {}
    for tid, category, res_time in cursor.fetchall():
        categories[int(tid)] = category
        resolution_times[int(tid)] = res_time
    
    cursor.close()
    conn.close()
    
    # Load embeddings
    embeddings_path = os.path.join(os.path.dirname(__file__), "../../data/generated/embeddings.npz")
    data = np.load(embeddings_path)
    ticket_ids = data['ticket_ids']
    embeddings = data['embeddings']
    
    print(f"Loaded {len(ticket_ids)} tickets from embeddings")
    print(f"Loaded {len(categories)} categories from MySQL")
    print(f"Ticket 12 category: {categories.get(12, 'NOT FOUND')}")
    
    # Create and save the explainer
    from app.explainability.similarity_explainer import SimilarityExplainer
    explainer = SimilarityExplainer(k=5)
    explainer.fit(ticket_ids, embeddings, categories, resolution_times)
    
    # Save
    save_path = os.path.join(os.path.dirname(__file__), "../../data/generated/similarity_explainer_fixed.joblib")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    explainer.save(save_path)
    print(f"Saved to {save_path}")
    
    # Test on ticket 12
    result = explainer.explain_by_ticket_id(12)
    print(f"\nTicket 12 neighbors:")
    for neighbor in result['similar_past_tickets']:
        print(f"  -> Ticket #{neighbor['ticket_id']} | {neighbor['category']} | similarity={neighbor['similarity']}")

if __name__ == "__main__":
    main()