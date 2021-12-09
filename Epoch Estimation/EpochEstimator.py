import matplotlib.pyplot as plt
import numpy as np
import re
import argparse
import sys
import time
import threading
import math
from scipy.optimize import curve_fit
import random


def __loss_fit_func(x, a, b, c):
    return (1/(a*x+b))+c

def _loss_curve_fitting(epochs_arr, losses_arr):
    param_bounds = ([0, 0, 0], [np.inf, np.inf, np.inf])
    sigma = np.ones(len(epochs_arr))
    NUM_SEGMENTS = 3
    for i in range(len(epochs_arr)):
        exp = int(math.floor(i/(math.ceil(1.0*len(epochs_arr)/NUM_SEGMENTS))))
        sigma[i] /= 4 ** exp
    
    params = curve_fit(__loss_fit_func, epochs_arr, losses_arr, sigma=np.array(sigma), absolute_sigma=False, bounds=param_bounds)
    return params[0]

def est_epoch(val_losses):
    if len(val_losses) >= 3:
        epoch_list = []
        loss_list = []
        for epoch, loss in val_losses.items():
            epoch_list.append(epoch)
            loss_list.append(loss)

        try:
            [a, b, c] = _loss_curve_fitting(epoch_list, loss_list)  # could throw exception since the loss may not descend at the beginning

        except Exception as e:
            print("loss curve fitting error: ", e)
            return -1
        epoch = 0      
        fitted_losses = []
        while True:
            fitted_losses.append(__loss_fit_func(epoch, a, b, c))
            flag = True
            if len(fitted_losses) >= 8:
                for i in reversed(range(8)):
                    if fitted_losses[epoch - i] - fitted_losses[epoch] > 0.005:
                        flag = False
                        break
            else:
                epoch +=1
                continue
            if not flag:
                epoch += 1
                if epoch > 100:  # each job must have at most 100 epochs
                    return -1
            else:
                return epoch
    else:
        return -1

def main():
    n = 5
    end_epoch = 6
    while n<=end_epoch:
        end_epoch =  est_epoch({k: loss_re[k] for k in idx[:n]})
        print("Curent Epoch:"+str(n)+"  Remaining Epoch:"+str(end_epoch-n))        
        n = n+1


LOSS_RE  = re.compile('.*?]\sTrain-cross-entropy=([\d\.]+)')

log = open("resnet110.log").read()

loss_re = [float(x) for x in LOSS_RE.findall(log)]
idx = np.arange(len(loss_re))
ep = 10
[a, b, c] = _loss_curve_fitting(idx[:ep], loss_re[:ep])
curvefitted = [__loss_fit_func(x,a,b,c) for x in idx]
plt.figure(figsize=(8, 6))
plt.xlabel("Epoch")
plt.ylabel("LOSS")
plt.plot(idx, loss_re, 'o', linestyle='-', color="b",
         label="Actual Training loss")
plt.plot(idx, curvefitted, 'o', linestyle='-', color="r",
         label="Predicted Training loss")
plt.legend(loc="best")
#plt.show()
main()
