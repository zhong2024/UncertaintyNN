from matplotlib.backends.backend_pdf import PdfPages

from data import sample_generators

import tensorflow as tf
import numpy as np
import plotting
import matplotlib.pyplot as plt

from training.combined_training import combined_training


def combined_evaluation(x, y, dropout, learning_rate, epochs, n_passes):
    """

    :param x:
    :param y:
    :param dropout:
    :param learning_rate:
    :param epochs:
    :param n_passes:
    :return:
    """
    sess, x_placeholder, dropout_placeholder = \
        combined_training(x, y, dropout, learning_rate, epochs)

    prediction_op = sess.graph.get_collection("prediction")
    log_variance = sess.graph.get_collection("log_variance")
    aleatoric_op = tf.exp(log_variance)

    x_eval = np.linspace(1.1 * np.min(x), 1.1 * np.max(x), 100).reshape([-1, 1])

    feed_dict = {x_placeholder: x_eval,
                 dropout_placeholder: dropout}

    predictions = []
    aleatorics = []
    for _ in range(n_passes):
        prediction, aleatoric = sess.run([prediction_op, aleatoric_op], feed_dict)
        predictions.append(prediction[0])
        aleatorics.append(aleatoric[0])

    y_eval = np.mean(predictions, axis=0).flatten()
    epistemic_eval = np.var(predictions, axis=0).flatten()
    aleatoric_eval = np.mean(aleatorics, axis=0).flatten()
    total_uncertainty_eval = epistemic_eval + aleatoric_eval

    fig, ax, = plotting.plot_mean_vs_truth(x, y,
                                           x_eval, y_eval, aleatoric_eval)
    fig.suptitle("Dropout - Learning Rate %f, Epochs %d, Dropout %f, Passes %d" %
                 (learning_rate, epochs, dropout, n_passes))

    ax.fill_between(x_eval.flatten(), 0, epistemic_eval, label="epistemic")
    ax.legend()
    sess.close()

    return fig, ax


def combined_osband_sin_evaluation(dropout, learning_rate, epochs, n_passes):
    x, y = sample_generators.generate_osband_sin_samples(60)
    fig, ax = combined_evaluation(x, y, dropout, learning_rate, epochs, n_passes)
    return fig, ax


def combined_osband_nonlinear_evaluation(dropout, learning_rate, epochs, n_passes):
    x, y = sample_generators.generate_osband_nonlinear_samples()
    fig, ax = combined_evaluation(x, y, dropout, learning_rate, epochs, n_passes)
    return fig, ax


if __name__ == "__main__":
    with PdfPages('Combined_Sinus.pdf') as pdf:
        for dropout in [0.3, 0.4, 0.5]:
            f, a = combined_osband_sin_evaluation(dropout, 1e-3, 20000, 100)
            pdf.savefig(f)
            plt.close()

    with PdfPages('Combined_Nonlinear.pdf') as pdf:
        for dropout in [0.3, 0.4, 0.5]:
            f, a = combined_osband_nonlinear_evaluation(dropout, 1e-3, 8000, 100)
            pdf.savefig(f)
            plt.close()