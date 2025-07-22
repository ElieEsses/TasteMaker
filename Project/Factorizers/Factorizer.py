from abc import ABC, abstractmethod
import pandas as pd

class Factorizer(ABC):
    @abstractmethod
    def fit_transform(self, matrix):
        pass

    @abstractmethod
    def save(self, path):
        pass

    def load(self, path) -> pd.DataFrame:
        pass