from sklearn.decomposition import TruncatedSVD
import joblib
from Factorizers.Factorizer import Factorizer

class SVD_Factorizer(Factorizer):
    def __init__(self, n_components=100):
        self.n_components = n_components
        self.model = TruncatedSVD(n_components=n_components, random_state=42)
        self.embeddings = None

    def fit_transform(self, matrix):
        self.embeddings = self.model.fit_transform(matrix)
        return self.embeddings

    def save(self, path):
        if self.embeddings is None:
            raise ValueError("Model has not been fit yet.")
        joblib.dump(self.embeddings, path)