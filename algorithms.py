from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import jaccard_score, pairwise
from sentence_transformers import SentenceTransformer  # Pour BERT
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD  # Pour LSA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import manhattan_distances
# Autres imports selon vos besoins...

import numpy as np

def image_selection_cosine(list_of_combined_texts, items, query):
    """
    Sélectionne l'image la plus pertinente en fonction des descriptions et de la requête initiale.

    :param list_of_combined_texts: Liste des descriptions des images.
    :param items: Liste des items (images) correspondants.
    :param query: Requête de recherche initiale.
    :return: URL de l'image la plus pertinente.
    """
    combined_texts = [query] + list_of_combined_texts
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(combined_texts)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    most_similar_idx = cosine_similarities.argsort()[0][-1]
    return items[most_similar_idx]['contentUrl']

def jaccard_similarity(query_vector, text_vectors):
    similarities = []
    for text_vector in text_vectors:
        intersection = np.logical_and(query_vector, text_vector)
        union = np.logical_or(query_vector, text_vector)
        similarity = np.sum(intersection) / np.sum(union)
        similarities.append(similarity)
    return similarities

def image_selection_jaccard(list_of_combined_texts, items, query):
    """
    Sélectionne l'image la plus pertinente en fonction des descriptions et de la requête initiale
    en utilisant la similarité de Jaccard.

    :param list_of_combined_texts: Liste des descriptions des images.
    :param items: Liste des items (images) correspondants.
    :param query: Requête de recherche initiale.
    :return: URL de l'image la plus pertinente.
    """
    vectorizer = CountVectorizer(binary=True)
    X = vectorizer.fit_transform(list_of_combined_texts).toarray()
    
    query_vector = X[0]  # Vecteur de la requête
    text_vectors = X[1:]  # Vecteurs des descriptions
    similarities = jaccard_similarity(query_vector, text_vectors)
    
    most_similar_idx = np.argmax(similarities)
    return items[most_similar_idx]['contentUrl']

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def image_selection_levenshtein(list_of_combined_texts, items, query):
    distances = [levenshtein_distance(query, text) for text in list_of_combined_texts]
    most_similar_idx = np.argmin(distances)
    return items[most_similar_idx]['contentUrl']

model_bert = SentenceTransformer('bert-base-nli-mean-tokens')

def bert_similarity(query, texts):
    embeddings = model_bert.encode([query] + texts)
    query_embedding = embeddings[0]
    text_embeddings = embeddings[1:]
    return cosine_similarity([query_embedding], text_embeddings)[0]

def image_selection_bert(list_of_combined_texts, items, query):
    similarities = bert_similarity([query] + list_of_combined_texts)
    most_similar_idx = np.argmax(similarities[0])
    return items[most_similar_idx]['contentUrl']

def lsa_similarity(query, texts):
    vectorizer = TfidfVectorizer()
    svd_model = TruncatedSVD(n_components=100)
    lsa = make_pipeline(vectorizer, svd_model, Normalizer(copy=False))

    embeddings = lsa.fit_transform([query] + texts)
    query_embedding = embeddings[0]
    text_embeddings = embeddings[1:]
    return cosine_similarity([query_embedding], text_embeddings)[0]

def image_selection_lsa(list_of_combined_texts, items, query):
    similarities = lsa_similarity([query] + list_of_combined_texts)
    most_similar_idx = np.argmax(similarities[0])
    return items[most_similar_idx]['contentUrl']


def manhattan_similarity(query, texts):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([query] + texts)
    query_embedding = tfidf_matrix[0]
    text_embeddings = tfidf_matrix[1:]
    # Manhattan distance returns a negative value, so we negate it to get similarity
    return -manhattan_distances([query_embedding], text_embeddings)[0]

def image_selection_manhattan(list_of_combined_texts, items, query):
    similarities = manhattan_similarity([query] + list_of_combined_texts)
    most_similar_idx = np.argmax(similarities[0])
    return items[most_similar_idx]['contentUrl']
