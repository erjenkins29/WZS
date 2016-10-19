
# coding: utf-8



from matplotlib import pyplot as plt
from numpy import *
import pandas as pd
import json

##### Generate plots around the result set


### Generate product.png, page.png, pageset.png

with open("output/importanceDict.txt",'r') as file:
    importanceDict = json.load(file)


i=1
for probtype in importanceDict.keys():
    #subplot(130+i)
    plt.figure(figsize=(3,5))
    vals = [val[1] for val in sorted(importanceDict[probtype].items())]
    plt.barh(range(len(importanceDict[probtype])), vals)
    plt.yticks(add(range(len(importanceDict[probtype])),.5), sorted(importanceDict[probtype].keys()))
    plt.xticks([])
    plt.title("Feature Importances - %s" % probtype)
    #i+=1
    plt.tight_layout()
    plt.savefig("images/%s.png"%probtype)
    plt.close()

### Generate feature_counts.png
    
plt.figure(figsize=(9,3))
plt.subplot(131); plt.hist(importanceDict["prod"].values(), range=(0,550), bins=10, histtype="stepfilled", color="g")
plt.title("prod")
plt.subplot(132); plt.hist(importanceDict["page"].values(), range=(0,550), bins=10, histtype="stepfilled", color="r")
plt.title("Distribution of feature counts (out of 550 solutions)\n\npage")
plt.subplot(133); plt.hist(importanceDict["pageset"].values(), range=(0,550), bins=10, histtype="stepfilled", color="purple")
plt.title("pageset")
plt.savefig("images/feature_counts.png")
plt.close()


with open("output/product_ms.txt",'r') as fh:
    Mprod = pd.Series(fh.read().split("\n")[:-1]).astype(int)
    
with open("output/page_ms.txt",'r') as fh:
    Mpage = pd.Series(fh.read().split("\n")[:-1]).astype(int)

with open("output/pageset_ms.txt",'r') as fh:
    Mpageset = pd.Series(fh.read().split("\n")[:-1]).astype(int)

### Generate Mdistributions.png

plt.figure(figsize=(7,6))
plt.style.use("seaborn-white")
plt.subplot(311); plt.hist(Mprod, range=(0,70), bins=40, color='g', histtype="stepfilled")
plt.title("Number of solutions found"); plt.ylabel("product");plt.yticks([])
plt.subplot(312); plt.hist(Mpage, range=(0,70), bins=40, color='r', histtype="stepfilled");plt.ylabel("page");plt.yticks([])
plt.subplot(313); plt.hist(Mpageset, range=(0,70), bins=40, color='purple', histtype="stepfilled");plt.ylabel("pageset");plt.yticks([])
plt.savefig("images/Mdistributions.png")
plt.close()



with open("output/atts.txt","r") as fh:
    atts = json.load(fh)
    
### Generate Adistributions_prod.png, Adistributions_page.png, Adistributions_pageset.png

for probtype in atts.keys():
    plt.figure(figsize=(11,6))
    keys = sorted(atts[probtype].keys())

    for i in range(5):
        for j in range(8):
            plt.subplot(5,8,8*i+j+1)
            plt.hist(atts[probtype][keys[8*i+j]],range=(0,10), bins=20)
            plt.title(keys[8*i+j][3:-3]); plt.xticks([]); plt.yticks([]) #; plt.ylim(0,100)
    plt.tight_layout()
    plt.savefig("images/Adistributions_%s.png" % probtype)
    plt.close()





