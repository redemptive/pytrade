import os
import json
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
# from sklearn.externals import joblib
import matplotlib.pyplot as plt
import numpy as np
from joblib import dump, load


class MLEngine:

    def __init__(self, model_name:str):
        data = MLEngine.load_model(model_name)
        self.model:object = data["model"]
        self.scaler = data["scaler"]
        self.details = data["details"]

    @staticmethod
    def prep_data(dataset, start, end, history_size):
        data = []
        labels = []
        for i in range(start, end):
            data.append(dataset[i, 0])
            labels.append(dataset[i - history_size:i, :])

        return np.array(data), np.array(labels)

    @staticmethod
    def build(df, feature_names, index, epochs, graph, name:str="test"):
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
        features = df[feature_names]
        features.index = df[index]

        TRAIN_SPLIT = int(len(df) / 3)
        BATCH_SIZE = 1
        BUFFER_SIZE = 10000

        scaler = MinMaxScaler()
        features_minmax = scaler.fit(features)
        dataset = scaler.transform(features)

        future_target = 1
        history_size = 7

        data_train, labels_train = MLEngine.prep_data(dataset, history_size, len(dataset) - TRAIN_SPLIT, history_size)
        data_val, labels_val = MLEngine.prep_data(dataset, len(dataset) - TRAIN_SPLIT, len(dataset), history_size)

        train_data = tf.data.Dataset.from_tensor_slices((labels_train, data_train))
        train_data = train_data.cache().shuffle(BUFFER_SIZE).batch(BATCH_SIZE).repeat()

        val_data = tf.data.Dataset.from_tensor_slices((labels_val, data_val))
        val_data = val_data.batch(BATCH_SIZE).repeat()

        model = tf.keras.models.Sequential()

        model.add(tf.keras.layers.LSTM(32,return_sequences=True,input_shape=(labels_train.shape[1], labels_train.shape[2])))
        model.add(tf.keras.layers.Dropout(0.2))

        model.add(tf.keras.layers.LSTM(50,return_sequences=True))
        model.add(tf.keras.layers.Dropout(0.2))

        model.add(tf.keras.layers.LSTM(50,return_sequences=True))
        model.add(tf.keras.layers.Dropout(0.2))

        model.add(tf.keras.layers.LSTM(16, activation='relu'))
        model.add(tf.keras.layers.Dense(future_target))

        model.compile(optimizer=tf.keras.optimizers.RMSprop(clipvalue=1.0), loss='mae')

        EVALUATION_INTERVAL = 1000

        # print(labels_val)
        # print(data_val)

        # history =
        model.fit(train_data, epochs=epochs, steps_per_epoch=EVALUATION_INTERVAL, validation_data=val_data, validation_steps=50)

        if graph:
            plt.plot(model.predict(labels_val))
            plt.plot(data_val)
            plt.show()

        details = {
            "epochs": epochs,
            "features": feature_names
        }

        MLEngine.save_model(name, model, features_minmax, details)

        return MLEngine(name)

    @staticmethod
    def load_model(name):
        with open(f"./ml_strategies/{name}/details.json") as raw:
            details = json.load(raw)

        return {
            "model": tf.keras.models.load_model(f"./ml_strategies/{name}"),
            "scaler": load(f"./ml_strategies/{name}/scaler.pkl"),
            "details": details
        }

    @staticmethod
    def save_model(name, model, scaler, details):
        model.save(f"./ml_strategies/{name}")
        dump(scaler, f"./ml_strategies/{name}/scaler.pkl")

        with open(f"./ml_strategies/{name}/details.json", "w") as outfile:
            json.dump(details, outfile)

    @staticmethod
    def create_time_steps(length):
        return list(range(-length, 0))