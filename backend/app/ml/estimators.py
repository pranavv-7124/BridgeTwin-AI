"""Learn annual deterioration instead of mainly copying the previous-health feature."""
import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin, clone

class ResidualHealthRegressor(RegressorMixin,BaseEstimator):
    def __init__(self,estimator): self.estimator=estimator

    def fit(self,X,y):
        self.estimator_=clone(self.estimator)
        loss=np.maximum(0,X['previous_health'].to_numpy()-np.asarray(y))
        self.estimator_.fit(X,loss)
        self.n_features_in_=self.estimator_.n_features_in_
        self.feature_names_in_=self.estimator_.feature_names_in_
        return self

    def predict(self,X):
        previous=X['previous_health'].to_numpy()
        return np.clip(previous-self.estimator_.predict(X),0,previous)

    @property
    def feature_importances_(self): return self.estimator_.feature_importances_
