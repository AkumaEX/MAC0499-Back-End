import pandas as pd
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression


class HotspotPredictor(object):

    def __init__(self, filepaths, n_clusters):
        def load_dataframe(filepath, month):
            cols = ['DATAOCORRENCIA', 'LATITUDE', 'LONGITUDE']
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

        def clear_dataframe(df):
            df.drop_duplicates(inplace=True)
            df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
            df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
            df.dropna(inplace=True)
            return df

        def get_dataframe():
            df = pd.concat(
                [load_dataframe(filepath, idx + 1)
                 for idx, filepath in enumerate(self._filepaths)]
            )
            df = clear_dataframe(df)
            df['GRUPO'] = self._kmeans.fit_predict(
                df[['LATITUDE', 'LONGITUDE']])
            return df

        def process_dataframe(df):
            df = df.groupby(['GRUPO', 'MES']).size().reset_index()
            df.columns = ['GRUPO', 'MES', 'COUNT']

            pipeline = ColumnTransformer([
                ('grupo', OneHotEncoder(categories=[
                    np.arange(self._n_clusters, dtype='int32')]), ['GRUPO']),
                ('mes', 'passthrough', ['MES'])
            ])
            X = pipeline.fit_transform(df)
            y = df['COUNT']
            return X, y

        def predict_hotspot():
            X_train, y_train = process_dataframe(self._df)
            threshold = y_train.median()

            lr = LinearRegression()
            lr.fit(X_train, y_train)
            X_pred = np.c_[np.identity(self._n_clusters), np.ones(
                self._n_clusters) * (len(self._filepaths) + 1)]
            y_pred = lr.predict(X_pred) >= threshold

            hotspot = dict()
            for i in range(self._n_clusters):
                hotspot[i] = y_pred[i]
            return hotspot

        self._filepaths = filepaths
        self._n_clusters = n_clusters
        self._kmeans = MiniBatchKMeans(
            n_clusters=n_clusters, init_size=n_clusters)
        self._df = get_dataframe()
        self._hotspot = predict_hotspot()

    def get_kmeans(self):
        return self._kmeans

    def get_df(self):
        return self._df

    def get_hotspot(self):
        return self._hotspot
