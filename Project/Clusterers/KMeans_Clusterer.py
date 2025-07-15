from sklearn.cluster import KMeans
import joblib
from Clusterers.Clusterer import Clusterer

class KMeans_Clusterer(Clusterer):
    def __init__(self, n_clusters=100, random_state=42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.model = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        self.labels = None

    def fit_predict(self, embeddings):
        self.labels = self.model.fit_predict(embeddings)
        return self.labels

    def save(self, path):
        if self.labels is None:
            raise ValueError("You need to run `fit_predict` first.")
        joblib.dump(self.labels, path)

    def save_model(self, path):
        joblib.dump(self.model, path)

    def load_model(self, path):
        self.model = joblib.load(path)