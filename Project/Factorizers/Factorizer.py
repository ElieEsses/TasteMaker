from abc import ABC, abstractmethod

class Factorizer(ABC):
    @abstractmethod
    def fit_transform(self, matrix):
        pass

    @abstractmethod
    def save(self, path):
        pass