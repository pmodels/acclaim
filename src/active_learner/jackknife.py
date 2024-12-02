# This file performs a jackknife variance calculation for a random forest regressor
# Portions of code borrowed from https://docs.astropy.org/en/stable/_modules/astropy/stats/jackknife.html 
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#   
#   Arguments:
#   $1 = pre-trained random forest regressor
#   $2 = test set X values

import csv

from sklearn import tree
from sklearn import neighbors
from sklearn.ensemble import RandomForestRegressor

import numpy as np
import sys

def jackknife_variances(regressor, X_test):
  trees = regressor.estimators_
  prediction_array = np.empty((len(trees), X_test.shape[0]))
  
  i = 0
  for tree in trees:
    predictions = tree.predict(X_test)
    prediction_array[i,:] = predictions
    i += 1

  means = np.mean(prediction_array, axis=0)
  variances = np.empty(means.shape)
  
  i = 0
  for column in prediction_array.T:
    mean = means[i]
    n = column.shape[0]

    resamples = np.empty((n,n-1))
    for j in range(n):
      resamples[j,:] = np.delete(column, j)
    
    resample_means = np.mean(resamples, axis=1)
    variances[i] = np.sum(np.square(np.subtract(resample_means, mean)))/(n*(n-1))
    i += 1
  
  return variances


def jackknife(regressor, X_test):
 
  variances = jackknife_variances(regressor, X_test)

  return np.average(variances)
