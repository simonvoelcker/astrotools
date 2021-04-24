import csv
import numpy as np

from tensorflow import keras
from tensorflow.keras import layers

x, y = [], []

with open('samples_1.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    for index, row in enumerate(reader):
        if index > 0:
            exposure, gain, yr, yg, yb, xr, xg, xb = row
            x.append([float(xr), float(xg), float(xb)])
            y.append([float(yr), float(yg), float(yb)])

num_training_samples = 2000

y_train = np.array(y[:num_training_samples])
x_train = np.array(x[:num_training_samples])
y_test = np.array(y[num_training_samples:])
x_test = np.array(x[num_training_samples:])

# Give the input an extra dimension for not-yet-understood reasons
x_train = np.expand_dims(x_train, -1)
x_test = np.expand_dims(x_test, -1)

input_shape = (3, 1)
batch_size = 100
epochs = 1000

model = keras.Sequential(
    [
        keras.Input(shape=input_shape),
        layers.Dense(256, activation="softmax"),
        layers.Flatten(),
        layers.Dropout(0.5),
        layers.Dense(3, activation="softmax"),
    ]
)

model.summary()

model.compile(loss="mean_squared_error", optimizer="adam", metrics=["accuracy"])

model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=0.1)

score = model.evaluate(x_test, y_test, verbose=0)

print("Test loss:", score[0])
print("Test accuracy:", score[1])

model.save("color_calib_model_1")
print("Model saved")
