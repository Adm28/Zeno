import os
import sys
import pandas as pd
import numpy as np
import re
import csv

baseDir = "Resnet_110-Cifar10_Logs"
df = pd.read_csv("resnet110.csv")
for filename in os.listdir(baseDir):
    if(filename.endswith('.log')):
        f = open(baseDir+"/"+filename,"r")
        epoch = 1
        ps=w=0
        y = re.search("[0-9]_[0-9]_[0-9]",filename)
        nums=y.group(0).split("_")
        ps=nums[1]
        w=nums[2]
        train_accuracy=train_cross_entropy=time_cost=validation_accuracy=validation_cross_entropy=is_validation_cross_entropy=0

        for line in f.readlines():
            is_flag=False
            if(re.search("Train-accuracy=[0-9]*.*[0-9]*",line)!=None):
                train_accuracy = re.search("Train-accuracy=[0-9]*.*[0-9]*",line).group(0).split("=")[1]
            if(re.search("Train-cross-entropy=[0-9]*.*[0-9]*",line)!=None):
                train_cross_entropy = re.search("Train-cross-entropy=[0-9]*.*[0-9]*",line).group(0).split("=")[1]
            if(re.search("Time cost=[0-9]*.*[0-9]*",line)!=None):
                time_cost = re.search("Time cost=[0-9]*.*[0-9]*",line).group(0).split("=")[1]
            if(re.search("Validation-accuracy=[0-9]*.*[0-9]*",line)!=None):
                validation_accuracy = re.search("Validation-accuracy=[0-9]*.*[0-9]*",line).group(0).split("=")[1]
            if(re.search("Validation-cross-entropy=[0-9]*.*[0-9]*",line)!=None):
                validation_cross_entropy = re.search("Validation-cross-entropy=[0-9]*.*[0-9]*",line).group(0).split("=")[1]
                is_flag=True
            if(is_flag==True):
                df=df.append(pd.Series(['2',epoch,ps,w,train_accuracy,train_cross_entropy,time_cost,validation_accuracy,validation_cross_entropy],index=df.columns),ignore_index=True)
                epoch+=1
df.to_csv("resnet110.csv",index=False)                