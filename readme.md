# TensorGeNN

A Python library for converting trained TensorFlow ANNs to GeNN spiking neural networks with low loss in performance using the algorithm proposed by *Diehl et al.* in "***Fast-Classifying, High-Accuracy Spiking Deep Networks Through Weight and Threshold Balancing***"

## Results
Below are the results of conversion experiments on MNIST and CIFAR-10 with and without data-based normalization.

### 1) MNIST
**ANN model**:\
Trained on 60000 examples for 5 epochs.\
Train accuracy: 99.21% on 60000 examples\
Test accuracy: 98.86% on 10000 examples

**GeNN model**:\
Conversion parameters:\
single_example_time = 350\
dense_membrane_capacitance = 1.0\
sparse_membrane_capacitance = 0.2\
neuron_threshold_voltage = -57.0\
neuron_resting_voltage = -60.0\

**On three trials**: (all accuracies on test set)\
Note: ANN test set contains 10000 example while the GeNN accuracies have been computed on 500 examples.

| ANN accuracy  | GeNN (without normalization) | GeNN (with normalization) |
| ------------- | ---------------------------- | ------------------------- |
| 98.91%        | 97.8%                        | 98.0%                     |
| 98.88%        | 96.8%                        | 97.2%                     |
| 98.88%        | 96.8%                        | 96.6%                     |

### 2) CIFAR-10
**ANN model**:\
Trained on 50000 examples for 10 epochs.\
Train accuracy: 90.99% on 50000 examples\
Test accuracy: 77.29% on 10000 examples (overfitting since I haven't added dropout layers yet)

**GeNN model**:\
Conversion parameters:\
single_example_time = 3750 (though it takes only ~2500 with no weight normalization)\
dense_membrane_capacitance = 0.1\
sparse_membrane_capacitance = 0.01\
neuron_threshold_voltage = -58.0\
neuron_resting_voltage = -60.0\

**On one trials**: (all accuracies on test set)\
Note: ANN test set contains 10000 example while the GeNN accuracies have been computed on 500 examples.

| ANN accuracy  | GeNN (without normalization) | GeNN (with normalization) |
| ------------- | ---------------------------- | ------------------------- |
| 77.29%        | 75.0%                        | 77.0%                     |

# Requirements:
- Python 3
- TensorFlow
- PyGeNN (see [here](https://github.com/genn-team/genn/blob/master/pygenn/README.md) for installation instructions)
- Matplotlib

# Installation:
Note: Since work is still in progress, we don't have a standard installation procedure. However, in the meantime, you can follow the steps below.
1. Clone the repository: `git clone https://github.com/genn-team/tensor_genn.git`
2. Change directory: `cd ~/tensor_genn`
3. Create a new file and follow a procedure shown in `conversion_example.py` to convert your TensorFlow model into GeNN.

# References:
- Peter U. Diehl, Daniel Neil, Jonathan Binas, Matthew Cook, Shih-Chii Liu, and Michael Pfeiffer. 2015. Fast-Classifying, High-Accuracy Spiking Deep Networks Through Weight and Threshold Balancing. IJCNN (2015)