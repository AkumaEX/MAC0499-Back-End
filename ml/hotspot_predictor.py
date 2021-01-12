import pandas as pd
import numpy as np
from scipy.spatial import Voronoi
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from joblib import dump


class HotspotPredictor(object):

    def __init__(self, filepaths, n_clusters):

        self._filepaths = filepaths
        self._n_clusters = n_clusters
        self._df = self._get_dataframe()
        self._kmeans = self._get_kmeans()
        self._hotspot = self._predict_hotspot()
        self._boundaries = self._create_boundaries()
        self._results = self._get_results()

    def get_kmeans(self):
        return self._kmeans

    def get_df(self):
        return self._df

    def get_hotspot(self):
        return self._hotspot

    def get_boundaries(self):
        return self._boundaries

    def save_kmeans_to(self, address):
        dump(self._kmeans, address)

    def get_results(self):
        return self._results

    def _get_kmeans(self):
        if self._n_clusters == 0:
            init_clusters = self._df[['BAIRRO', 'CIDADE', 'LATITUDE', 'LONGITUDE']].groupby(
                ['CIDADE', 'BAIRRO']).mean().dropna().to_numpy()
            self._n_clusters, _ = init_clusters.shape
            return MiniBatchKMeans(n_clusters=self._n_clusters, init_size=self._n_clusters, max_iter=10000,
                                   init=init_clusters)
        else:
            return MiniBatchKMeans(n_clusters=self._n_clusters, init_size=self._n_clusters, max_iter=10000)

    @staticmethod
    def _load_dataframe(filepath, month):
        cols = ['DATAOCORRENCIA', 'HORAOCORRENCIA', 'BAIRRO', 'CIDADE', 'LATITUDE', 'LONGITUDE']
        df = pd.read_csv(
            filepath_or_buffer=filepath,
            encoding='utf-16 le',
            delimiter='\t',
            decimal=',',
            dayfirst=True,
            usecols=cols
        )
        df['MES'] = month
        return df

    @staticmethod
    def _clear_dataframe(df):
        df.drop_duplicates(inplace=True)
        df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
        df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
        df.dropna(inplace=True)
        return df

    def _get_dataframe(self):
        df = pd.concat([self._load_dataframe(filepath, idx + 1) for idx, filepath in enumerate(self._filepaths)])
        return self._clear_dataframe(df)

    def _process_dataframe(self, df):
        df['GRUPO'] = self._kmeans.fit_predict(df[['LATITUDE', 'LONGITUDE']])
        df = df.groupby(['GRUPO', 'MES']).size().reset_index()
        df.columns = ['GRUPO', 'MES', 'COUNT']

        pipeline = ColumnTransformer([
            ('grupo', OneHotEncoder(categories=[np.arange(self._n_clusters, dtype='int32')]), ['GRUPO']),
            ('mes', 'passthrough', ['MES'])
        ])
        X = pipeline.fit_transform(df)
        y = df['COUNT']
        return X, y

    def _predict_hotspot(self):
        X_train, y_train = self._process_dataframe(self._df)
        threshold = y_train.median()

        lr = LinearRegression()
        lr.fit(X_train, y_train)
        X_pred = np.c_[np.identity(self._n_clusters), np.ones(self._n_clusters) * (len(self._filepaths) + 1)]
        y_pred = lr.predict(X_pred) >= threshold

        hotspot = dict()
        for i in range(self._n_clusters):
            hotspot[i] = y_pred[i]
        return hotspot

    def _get_results(self):
        results = []
        for cluster in range(self._n_clusters):
            df = self._df[self._df['GRUPO'] == cluster]
            features = [self._get_point(row['LATITUDE'], row['LONGITUDE'], row['DATAOCORRENCIA'], row['HORAOCORRENCIA'],
                                        cluster) for idx, row in df.iterrows()]
            features.append(self._get_boundary(cluster))
            results.append(self._get_feature_collection(features, cluster))
        return results

    def _get_point(self, latitude, longitude, date, time, cluster):
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [latitude, longitude]
            },
            'properties': {
                'date': date,
                'time': time
            },
            'hotspot': bool(self._hotspot[cluster]),
            'cluster': cluster
        }

    def _get_boundary(self, cluster):
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': self._boundaries.get(cluster, [])
            },
            'hotspot': bool(self._hotspot[cluster]),
            'cluster': cluster
        }

    def _get_feature_collection(self, features, cluster):
        return {
            'type': 'FeatureCollection',
            'features': features,
            'hotspot': bool(self._hotspot[cluster]),
            'cluster': cluster
        }

    @staticmethod
    def voronoi_finite_polygons_2d(vor, radius=None):
        if vor.points.shape[1] != 2:
            raise ValueError("Requires 2D input")

        new_regions = []
        new_vertices = vor.vertices.tolist()

        center = vor.points.mean(axis=0)
        if radius is None:
            radius = vor.points.ptp().max() * 2

        all_ridges = {}
        for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
            all_ridges.setdefault(p1, []).append((p2, v1, v2))
            all_ridges.setdefault(p2, []).append((p1, v1, v2))

        for p1, region in enumerate(vor.point_region):
            vertices = vor.regions[region]

            if all([v >= 0 for v in vertices]):
                new_regions.append(vertices)
                continue

            ridges = all_ridges.get(p1, [])
            new_region = [v for v in vertices if v >= 0]

            for p2, v1, v2 in ridges:
                if v2 < 0:
                    v1, v2 = v2, v1
                if v1 >= 0:
                    continue

                t = vor.points[p2] - vor.points[p1]
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])

                midpoint = vor.points[[p1, p2]].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[v2] + direction * radius

                new_region.append(len(new_vertices))
                new_vertices.append(far_point.tolist())

            vs = np.asarray([new_vertices[v] for v in new_region])
            c = vs.mean(axis=0)
            angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
            new_region = np.array(new_region)[np.argsort(angles)]
            new_regions.append(new_region.tolist())

        return new_regions, np.asarray(new_vertices)

    def _create_boundaries(self):
        boundaries = {}
        points = self._kmeans.cluster_centers_
        clusters = self._kmeans.predict(points)
        vor = Voronoi(points)
        regions, vertices = self.voronoi_finite_polygons_2d(vor)
        for cluster, region in zip(clusters, regions):
            boundaries[cluster] = vertices[region].tolist()
        return boundaries
