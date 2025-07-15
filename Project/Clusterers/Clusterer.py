from abc import ABC, abstractmethod

class Clusterer(ABC):
    @abstractmethod
    def fit_predict(self, embeddings):
        pass

    @abstractmethod
    def save(self, path):
        pass