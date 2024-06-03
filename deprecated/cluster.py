from typing import List
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm
from typing import List
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pickle

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

def load_word_embeddings(file_path) -> dict:
    with open(file_path, 'rb') as f:
        model = pickle.load(f)
    return model
word_embeddings = load_word_embeddings("w2v/word2vec-google-news-300/word2vec-google-news-300.model")

def preprocess_text(text: str) -> str:
    tokens = word_tokenize(text.lower())
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalpha()]
    clean_tokens = [token for token in lemmatized_tokens if token not in stopwords.words('english')]
    return clean_tokens

def find_optimal_clusters(data, max_k=10):
    iters = range(2, min(max_k + 1, data.shape[0]))
    sse = []
    for k in tqdm(iters, total=len(iters), desc="Finding optimal K clusters"):
        model = KMeans(n_clusters=k, random_state=42)
        model.fit(data)
        sse.append(model.inertia_) # Sum of squared distances of samples to their closest cluster center
    return iters[np.argmin(sse)]

def cluster(reqs: List[str]) -> List[str]:
    # Step 1: Preprocess each requirement
    X = []
    for req in reqs:
        tokens = preprocess_text(req)
        req_embedding = np.mean([word_embeddings.get(token, np.zeros(word_embeddings.vector_size)) for token in tokens], axis=0)
        X.append(req_embedding)
    # Step 2: Determine the optimal number of clusters
    optimal_k = find_optimal_clusters(np.array(X), max_k=10)
    print(f"Optimal number of clusters: {optimal_k}")
    # Step 3: Clustering with optimal number of clusters
    model = KMeans(n_clusters=optimal_k, random_state=52)
    model.fit(X)
    # Step 4: Creating cluster labels
    labels = model.labels_
    cluster_labels = [f"Cluster {label + 1}" for label in labels]
    return cluster_labels

# Example usage
requirements = [
    "User can login using email and password",
    "The system shall provide encrypted data storage",
    "Implement password recovery feature",
    "System must perform data backup every 24 hours",
    "User shall be able to export data as CSV",
    "Ensure the user interface is responsive on mobile devices",
]

if __name__ == "__main__":
    print(cluster(requirements))

