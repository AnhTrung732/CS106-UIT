from test import *
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import numpy as np

def process_visual(name) :
    name_file = Test(name).load()
    value = []
    weight = []

    with open(name_file) as test_file:
        rows = test_file.read().split('\n')
    #print(rows)
    for row in rows:
        try:
            row_1, row_2 = row.split(" ")
            value.append(int(row_1))
            weight.append(int(row_2))
        except Exception:
            pass
    return (value,weight)


def visual(save_dir,name=None,value=None,weight=None) :
    # Visual after solve
    if value==None and weight==None :
        value,weight = process_visual(name)
    plt.scatter(weight,value, c="blue")
    plt.title('Value-Weight')
    plt.xlabel("Weight")
    plt.ylabel("Values")
    plt.savefig(save_dir + name + '.png')
    plt.clf()

if __name__ == '__main__':

    for i in range (0,13):
                for j in [50,100,200,500,1000,2000,5000,10000] :
                    for k in [0,1] :
                        for l in  range(0,100):
                            name = str(i) + '-' + str(j) + '-' + str(k) + '-' + str(l)
                            save_dir = "visual/input/"
                            visual(save_dir,name=name,value=None,weight=None)