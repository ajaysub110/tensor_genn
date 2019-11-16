import tensorflow as tf
import tensorflow.keras.backend as K

import tensor_genn as tg
from tensor_genn.algorithms import ReLUANN
from tensor_genn.algorithms.weight_normalization import DataBased
from tensor_genn.utils.plotting import raster_plot

def train_mnist():
    mnist = tf.keras.datasets.mnist

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train_normed, x_test_normed = x_train / 255.0, x_test / 255.0

    x_train_normed, x_test_normed = x_train_normed.reshape((-1,28,28,1)), x_test_normed.reshape((-1,28,28,1))
    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(16,5,padding='valid',activation='relu',use_bias=False,input_shape=(28,28,1)),
        tf.keras.layers.AveragePooling2D(2),
        tf.keras.layers.Conv2D(8,5,padding='same',activation='relu',use_bias=False),
        tf.keras.layers.Flatten(input_shape=(28,28,1)),
        tf.keras.layers.Dense(128, activation='relu', use_bias=False),
        tf.keras.layers.Dense(64, activation='relu', use_bias=False),
        tf.keras.layers.Dense(10, activation='softmax',use_bias=False)
    ])

    model.compile(optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

    model.fit(x_train_normed[:10000], y_train[:10000], epochs=1)

    model.evaluate(x_test_normed[:10000], y_test[:10000])

    print(model.summary())

    return model, x_train_normed, y_train, x_test_normed, y_test

def train_cifar10():
    cifar10 = tf.keras.datasets.cifar10

    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    x_train_normed, x_test_normed = x_train / 255.0, x_test / 255.0

    x_train_normed, x_test_normed = x_train_normed.reshape((-1,32,32,3)), x_test_normed.reshape((-1,32,32,3))

    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(32,3,padding='same',activation='relu',use_bias=False,input_shape=(32,32,3)),
        tf.keras.layers.Conv2D(32,3,padding='same',activation='relu',use_bias=False),
        tf.keras.layers.AveragePooling2D(2),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Conv2D(64,3,padding='same',activation='relu',use_bias=False),
        tf.keras.layers.Conv2D(64,3,padding='same',activation='relu',use_bias=False),
        tf.keras.layers.AveragePooling2D(2),
        tf.keras.layers.Conv2D(128,3,padding='same',activation='relu',use_bias=False),
        tf.keras.layers.Conv2D(128,3,padding='same',activation='relu',use_bias=False),
        tf.keras.layers.AveragePooling2D(2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(128, activation='relu', use_bias=False),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(10, activation='softmax',use_bias=False)
    ])

    model.compile(optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

    model.fit(x_train_normed, y_train, epochs=0)

    # model.evaluate(x_test_normed[:10000], y_test[:10000])

    print(model.summary())

    return model, x_train_normed, y_train, x_test_normed, y_test

tf_model, x_train, y_train, x_test, y_test = train_cifar10()

tf_model = tf.keras.models.load_model('cifar_tf_model.h5')

# Sample conversion
relu_ann = ReLUANN(single_example_time=100.,dense_membrane_capacitance=0.1,sparse_membrane_capacitance=0.5,neuron_threshold_voltage=-56.0)
data_based = DataBased(data=x_train.reshape((-1,32,32,1)))
g_model, spike_ids, spike_times, neuron_pops, syn_pops = tg.convert_model(
    tf_model,relu_ann,x_test[:100],y_test[:100], data_based, save_example_spikes=[20]
)
raster_plot(spike_ids, spike_times, neuron_pops)
