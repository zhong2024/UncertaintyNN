from matplotlib.backends.backend_pdf import PdfPages
from data import sample_generators

import numpy as np
import plotting
import matplotlib.pyplot as plt

from training.dropout_training import dropout_training


def dropout_evaluation(x, y, dropout, learning_rate, epochs, n_passes):
    sess, x_placeholder, dropout_placeholder = \
        dropout_training(x, y, dropout, learning_rate, epochs)

    prediction_op = sess.graph.get_collection("prediction")

    x_eval = np.linspace(1.1 * np.min(x), 1.1 * np.max(x), 100).reshape([-1, 1])

    feed_dict = {x_placeholder: x_eval,
                 dropout_placeholder: dropout}

    predictions = []
    for _ in range(n_passes):
        predictions.append(sess.run(prediction_op, feed_dict)[0])

    y_eval = np.mean(predictions, axis=0).flatten()
    uncertainty_eval = np.var(predictions, axis=0).flatten()

    fig, ax, = plotting.plot_mean_vs_truth(x, y,
                                           x_eval, y_eval, uncertainty_eval)

    return fig, ax


def dropout_osband_sin_evaluation(dropout, learning_rate, epochs, n_passes):
    x, y = sample_generators.generate_osband_sin_samples()
    fig, ax = dropout_evaluation(x, y, dropout, learning_rate, epochs, n_passes)
    return fig, ax


def dropout_osband_nonlinear_evaluation(dropout, learning_rate, epochs, n_passes):
    x, y = sample_generators.generate_osband_nonlinear_samples()
    fig, ax = dropout_evaluation(x, y, dropout, learning_rate, epochs, n_passes)
    return fig, ax


if __name__ == "__main__":
    with PdfPages('Dropout_Sinus.pdf') as pdf:
        for dropout in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            f, a = dropout_osband_sin_evaluation(dropout, 1e-3, 20000, 100)
            pdf.savefig(f)
            plt.close()

    with PdfPages('Dropout_Nonlinear.pdf') as pdf:
        for dropout in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            f, a = dropout_osband_nonlinear_evaluation(dropout, 1e-3, 8000, 100)
            pdf.savefig(f)
            plt.close()
