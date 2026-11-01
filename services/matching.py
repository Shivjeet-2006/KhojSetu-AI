
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@st.cache_resource
def load_model():
    return SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2"
    )


def normalize(value):
    return str(value or "").strip().lower()


def find_matches(lost_description, found_items, top_k=3,
                 lost_item=None):

    if not lost_description or not found_items:
        return []

    model = load_model()

    lost_item = lost_item or {}
    found_descriptions = [
        item.get("description", "") for item in found_items
    ]

    embeddings = model.encode(
        [lost_description] + found_descriptions
    )

    description_scores = cosine_similarity(
        [embeddings[0]], embeddings[1:]
    )[0]

    results = []

    for item, similarity in zip(found_items, description_scores):

        # AI description similarity
        description_score = max(0, float(similarity))

        # Category match
        lost_category = normalize(lost_item.get("category"))
        found_category = normalize(item.get("category"))

        category_score = (
            1.0 if lost_category and lost_category == found_category
            else 0.0
        )

        # Color match
        lost_color = normalize(lost_item.get("color"))
        found_color = normalize(item.get("color"))

        color_score = (
            1.0 if lost_color and lost_color == found_color
            else 0.0
        )

        # Location similarity (simple text comparison)
        lost_location = normalize(lost_item.get("location"))
        found_location = normalize(item.get("location"))

        location_score = (
            1.0 if lost_location and found_location
            and (
                lost_location in found_location
                or found_location in lost_location
            )
            else 0.0
        )

        # Identifying details
        lost_details = normalize(
            lost_item.get("identifying_details")
        )
        found_details = normalize(
            item.get("identifying_details")
        )

        details_score = (
            1.0 if lost_details and found_details
            and (
                lost_details in found_details
                or found_details in lost_details
            )
            else 0.0
        )

        # Weighted score
        score = (
            0.40 * description_score
            + 0.20 * category_score
            + 0.15 * color_score
            + 0.15 * location_score
            + 0.10 * details_score
        )

        results.append({
            "item": item,
            "similarity_score": round(score * 100, 2),
            "description_score": round(description_score * 100, 2),
            "category_match": bool(category_score),
            "color_match": bool(color_score),
            "location_match": bool(location_score),
            "details_match": bool(details_score)
        })

    results.sort(
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    return results[:top_k]
