import os
import sys
import pandas as pd
import numpy as np
import re
import csv


for filename in os.listdir():
    if(filename.endswith(".log")):
        f = open(filename,"r")
        total_cost=0.0
        count = 0
        ps=0
        w=0
        y = re.search("[0-9]_[0-9]_[0-9]",filename)
        if(y!=None):
            nums=y.group(0).split("_")
            ps=nums[1]
            w=nums[2]
        for line in f.readlines():
            x = re.search("cost=[0-9]*.[0-9]*",line)
            if(x!=None):
                count+=1
                x = x.group().split("=")
                total_cost += float(x[1])
        print("total_cost = "+str((total_cost)/count))
        with open("/Users/amishra19/Documents/Final Year Project - Logs/Logs(Gcloud-2-core-8-Gb)/CleanedEpochTime.csv","a+") as epochfile:
            epochwriter = csv.writer(epochfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            #first arg is the workload_id
            epochwriter.writerow(['1',ps,w,(total_cost)/count])
