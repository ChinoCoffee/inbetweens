import numpy as np
import GPy

"""
RBF kernel

  cov( x_i, x_j | alpha, beta ) = alpha * exp ( -0.5 * beta * || x_i - x_j || ^ 2 )

  where
    alpha : the variance
    beta  : length-scale

"""

"""
some optimizers I tried

    #kernel = GPy.kern.RBF(input_dim, variance=0.00001, lengthscale=20) + GPy.kern.Bias(input_dim')
    #kernel = GPy.kern.RBF(input_dim) + GPy.kern.White(input_dim, variance=0.5)

    #model = GPy.models.SparseGPLVM(X, input_dim, kernel=kernel, num_inducing=6)

    #model.optimize(messages=True, max_iters=1e4, optimizer='bfgs', gtol=.05)

    #model.optimize(messages=True, max_iters=5e3, optimizer='tnc')
    #model.optimize(messages=True, max_iters=5e3, optimizer='lbfgs')
"""


def calculate_manifold(data):
    X = np.copy(data)
    X_mean = X.mean(0)
    X -= X_mean

    input_dim = 2   # How many latent dimensions to use

    kernel = GPy.kern.RBF(input_dim)
    model = GPy.models.BayesianGPLVM(X, input_dim, kernel=kernel, num_inducing=6)
    model.optimize(messages=True, max_iters=5e3, optimizer='scg')

    return model, X_mean
