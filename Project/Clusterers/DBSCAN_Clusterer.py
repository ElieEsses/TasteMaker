from sklearn.cluster import DBSCAN
import joblib
from Clusterers.Clusterer import Clusterer

class DBSCAN_Clusterer(Clusterer):
    def __init__(self, eps=1.2, min_samples=10, metric='cosine'):
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric
        self.model = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric=self.metric)
        self.labels = None

    def fit_predict(self, embeddings):
        self.labels = self.model.fit_predict(embeddings)
        return self.labels

    def save(self, path):
        if self.labels is None:
            raise ValueError("You need to run `fit_predict` first.")
        joblib.dump(self.labels, path)