
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Multilingual model for Hindi, English and other languages
model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def find_matches(lost_description, found_items, top_k=3):

    if not lost_description or not found_items:
        return []

    # Extract descriptions of found items
    descriptions = [
        item["description"] for item in found_items
    ]

    # Convert descriptions into numerical embeddings
    lost_embedding = model.encode([lost_description])
    found_embeddings = model.encode(descriptions)

    # Calculate similarity scores
    scores = cosine_similarity(
        lost_embedding,
        found_embeddings
    )[0]

    results = []

    for item, score in zip(found_items, scores):
        results.append({
            "item": item,
            "similarity_score": round(float(score) * 100, 2)
        })

    # Show highest matching items first
    results.sort(
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    return results[:top_k]
