from abc import ABC, abstractmethod
from typing import Dict, Optional
import pandas as pd
import numpy as np


class ForecastingStrategy(ABC):
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.is_trained = False
        self.metrics = {}
        
    @abstractmethod
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> 'ForecastingStrategy':
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        pass
    
    @abstractmethod
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        pass
    
    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        return None
    
    def save_model(self, filepath: str) -> None:
        import pickle
        if not self.is_trained:
            raise ValueError("Model chưa được huấn luyện")
        
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    def load_model(self, filepath: str) -> None:
        import pickle
        with open(filepath, 'rb') as f:
            loaded = pickle.load(f)
            self.__dict__.update(loaded.__dict__)
        self.is_trained = True
    
    def get_metrics(self) -> Dict[str, float]:
        return self.metrics.copy()
    
    def __str__(self) -> str:
        status = "Đã huấn luyện" if self.is_trained else "Chưa huấn luyện"
        return f"{self.name} ({status})"
    
    def __repr__(self) -> str:
        return f"ForecastingStrategy(name='{self.name}', is_trained={self.is_trained})"
