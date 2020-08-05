import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np

from obj.Data import Data


class MLEngine:

    @staticmethod
    def build(df, features, index):
        features = df[features]
        features.index = df[index]

        TRAIN_SPLIT = int(len(df) - (len(df) / 3))
        BATCH_SIZE = 32
        BUFFER_SIZE = 10000

        scaler = MinMaxScaler()
        features_minmax = scaler.fit(features)
        dataset = scaler.transform(features)

        #dataset = dataset.values
        # data_mean = dataset[:TRAIN_SPLIT].mean(axis=0)
        # data_std = dataset[:TRAIN_SPLIT].std(axis=0)
        # dataset = (dataset-data_mean)/data_std

        future_target = 7
        x_train, y_train = Data.prep_ml_data(dataset, dataset[:, 0], 31,
                                                        TRAIN_SPLIT, 7,
                                                        future_target, 1)
        x_val, y_val = Data.prep_ml_data(dataset, dataset[:, 0],
                                                    TRAIN_SPLIT, None, 7,
                                                    future_target, 1)

        train_data = tf.data.Dataset.from_tensor_slices((x_train, y_train))
        train_data = train_data.cache().shuffle(BUFFER_SIZE).batch(BATCH_SIZE).repeat()

        val_data = tf.data.Dataset.from_tensor_slices((x_val, y_val))
        val_data = val_data.batch(BATCH_SIZE).repeat()

        model = tf.keras.models.Sequential()

        model.add(tf.keras.layers.LSTM(32,return_sequences=True,input_shape=x_train.shape[-2:]))
        model.add(tf.keras.layers.Dropout(0.2))

        model.add(tf.keras.layers.LSTM(50,return_sequences=True))
        model.add(tf.keras.layers.Dropout(0.2))

        model.add(tf.keras.layers.LSTM(50,return_sequences=True))
        model.add(tf.keras.layers.Dropout(0.2))

        model.add(tf.keras.layers.LSTM(16, activation='relu'))
        model.add(tf.keras.layers.Dense(7))

        model.compile(optimizer=tf.keras.optimizers.RMSprop(clipvalue=1.0), loss='mae')

        EVALUATION_INTERVAL = 200
        EPOCHS = 10


        history = model.fit(train_data, epochs=EPOCHS,
                                          steps_per_epoch=EVALUATION_INTERVAL,
                                          validation_data=val_data,
                                          validation_steps=50)

        print(dataset)
        for x, y in val_data:
            MLEngine.multi_step_plot(x[0], y[0], model.predict(x)[0])

        return model

    @staticmethod
    def multi_step_plot(history, true_future, prediction):
        plt.figure(figsize=(12, 6))
        num_in = MLEngine.create_time_steps(len(history))
        num_out = len(true_future)

        plt.plot(num_in, np.array(history[:, 1]), label='History')
        plt.plot(np.arange(num_out)/1, np.array(true_future), 'bo',
                label='True Future')
        if prediction.any():
            plt.plot(np.arange(num_out)/1, np.array(prediction), 'ro',
                    label='Predicted Future')
        plt.legend(loc='upper left')
        plt.show()

    @staticmethod
    def create_time_steps(length):
        return list(range(-length, 0))
