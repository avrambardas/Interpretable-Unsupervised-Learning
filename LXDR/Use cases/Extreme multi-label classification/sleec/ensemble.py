import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from helpers import project


class Model():
    def __init__(self, cluster_models, train_Y):
        self.models = cluster_models
        self.train_Y = train_Y
        
    def closet_cluster(self, x):
        sims = []
        for m in self.models:
            z = project(m['V'], x)  # the projected value
            sim = cosine_similarity([z], [m['center_z']])
            sims.append(sim)
        return self.models[np.argmax(sims)]
    
    def predict(self, x):
        model = self.closet_cluster(x)
        z = project(model['V'], x)
        dist, nbrs = model['Z_neighbors'].kneighbors([z], return_distance=True)
        real_idx = [model['data_idx'][i] for i in nbrs[0]]

        # weight by 1 / distance
        weights = (1 / dist).T
        labels = np.asarray(self.train_Y[real_idx, :].todense())
        # print(weights.shape)
        # print(labels.shape)
        # print(type(weights))
        # print(type(labels))
        scores_per_instance = labels * weights
        scores = scores_per_instance.sum(axis=0)
        return np.array(scores).flatten()


class Ensemble():
    def __init__(self, models):
        self.models = models
        
    def predict_one(self, x):
        preds = np.array([m.predict(x) for m in self.models])
        label_scores = np.array(preds.sum(0))
        return label_scores
    
    def predict_many(self, X):
        return np.array([
            self.predict_one(X[i, :])
            for i in tqdm(range(X.shape[0]))
        ])

