import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np


class MLEngine:

    def __init__(self, model:object, details:dict):
        self.model:object = model
        self.details:dict = details

    @staticmethod
    def build(df, features, index, name:str="test"):
        features = df[features]
        features.index = df[index]

        TRAIN_SPLIT = int(len(df) / 3)
        BATCH_SIZE = 7
        BUFFER_SIZE = 10000

        scaler = MinMaxScaler()
        features_minmax = scaler.fit(features)
        dataset = scaler.transform(features)

        future_target = 1
        history_size = 7

        data_train = []
        labels_train = []
        data_val = []
        labels_val = []

        for i in range(history_size, len(dataset) - TRAIN_SPLIT):
            data_train.append(dataset[i, 0])
            labels_train.append(dataset[i-history_size:i, :])

        for i in range(len(dataset) - TRAIN_SPLIT, len(dataset)):
            data_val.append(dataset[i, 0])
            labels_val.append(dataset[i-history_size:i, :])

        data_train = np.array(data_train)
        labels_train = np.array(labels_train)

        data_val = np.array(data_val)
        labels_val = np.array(labels_val)

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
        EPOCHS = 10

        print(labels_val)
        print(data_val)

        history = model.fit(train_data, epochs=EPOCHS,
                                          steps_per_epoch=EVALUATION_INTERVAL,
                                          validation_data=val_data,
                                          validation_steps=50)
        plt.plot(model.predict(labels_val))
        plt.plot(data_val)
        plt.show()
        #for i in range(len(data_val)):
            #print(f"Real: {data_val[i]} Predicted: {model.predict(labels_val)[i]}")

        model.save(f"./ml_strategies/{name}")

        return model

    @staticmethod
    def prep_ml_data(dataset, target, start_index, end_index, history_size,
                      target_size, step, single_step=False):
        data = []
        labels = []

        start_index = start_index + history_size
        if end_index is None:
            end_index = len(dataset) - target_size

        for i in range(start_index, end_index):
            indices = range(i-history_size, i, step)
            data.append(dataset[indices])

            if single_step:
                labels.append(target[i+target_size])
            else:
                labels.append(target[i:i+target_size])

        return np.array(data), np.array(labels)


    @staticmethod
    def multi_step_plot(history, true_future, prediction):
        plt.figure(figsize=(12, 6))
        num_in = MLEngine.create_time_steps(len(history))
        num_out = len(true_future)

        plt.plot(num_in, np.array(history[:, 1]), label='History')
        plt.plot(np.arange(num_out)/1, np.array(true_future), 'ro',
                label='True Future')
        if prediction.any():
            plt.plot(np.arange(num_out)/1, np.array(prediction), 'go',
                    label='Predicted Future')
        plt.legend(loc='upper left')
        plt.show()

    @staticmethod
    def create_time_steps(length):
        return list(range(-length, 0))
