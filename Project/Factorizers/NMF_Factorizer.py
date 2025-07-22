from sklearn.decomposition import NMF
from scipy.sparse import csr_matrix
from Factorizers.Factorizer import Factorizer
import joblib
import pandas as pd

class NMF_Factorizer(Factorizer):
    def __init__(self, n_components=100):
        self.n_components = n_components
        self.model = NMF(n_components=n_components, init='nndsvda', random_state=42)
        self.embeddings = None

    def fit_transform(self, matrix):
        if not isinstance(matrix, csr_matrix):
            matrix = matrix.tocsr()
        self.embeddings = self.model.fit_transform(matrix)
        return self.embeddings

    def save(self, path):
        if self.embeddings is None:
            raise ValueError("Model has not been fit yet.")
        joblib.dump(self.embeddings, path)

    def load(self, path) -> pd.DataFrame:
        data = path
        df = pd.DataFrame(data)

        return df
