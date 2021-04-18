import random
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

# Model / data parameters
input_shape = (3, 1)
train_samples = 20000
test_samples = 2000


def generate_random_color():
    return [
        random.random(),
        random.random(),
        random.random(),
    ]


def get_distorted_color(color):
    return [
        0.5 * color[0] + 0.4 * color[1] + 0.1 * color[2],
        0.2 * color[0] + 0.2 * color[1] + 0.6 * color[2],
        0.3 * color[0] + 0.4 * color[1] + 0.3 * color[2],
    ]


y_train = np.array([generate_random_color() for _ in range(train_samples)])
x_train = np.array([get_distorted_color(c) for c in y_train])

y_test = np.array([generate_random_color() for _ in range(test_samples)])
x_test = np.array([get_distorted_color(c) for c in y_test])

# Give the input an extra dimension for not-yet-understood reasons
x_train = np.expand_dims(x_train, -1)
x_test = np.expand_dims(x_test, -1)

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

batch_size = 100
epochs = 20

model.compile(loss="mean_squared_error", optimizer="adam", metrics=["accuracy"])

model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=0.1)

score = model.evaluate(x_test, y_test, verbose=0)
print("Test loss:", score[0])
print("Test accuracy:", score[1])
