
# coding: utf-8

import time
import json
import pandas as pd
import rankLP as rlp
import re
from matplotlib import pyplot as plt
from pulp import GLPK, PULP_CBC_CMD
#from emailnotice import emailEvan

####INSERT NOTE to add to your email here:
##
##
msgtoinclude = """
test case: 
add normalizer.  NOTE:  fixed issue-- normalizer was normalizing the page, not allowing the page/pageset functions to complete
add flip rank columns -- (let the high ranks like 17 be large numbers, low ranks like 4000 be small numbers)

lbound_v = 1
changed thresh = .02
Add dictionary of hasAtt --> chinese names to this email message
Added dummy columns
REMOVE the following columns: 
["agg02","featagg08", "featagg02", 
u'rank7', u'rank14', u'rank60', 
u'c28', u'c30', u'c34', u'c45',
"positive_comment_num","negative_comment_num","medium_comment_num", 
"is_in_stock"]
ADDED atts.txt


IMPORTANT: Created a new script, which loops 9 times, for different values of threshbin and threshint -- emailing me everytime

To do:
Add a method to resultsToIMG.py that histograms the a_i values, then in runall.sh backup the image and file
"""
##
##
######


#Rank by Product, Page, and Pageset
scriptStartTime = time.time()

####2016-10-09 [Evan] Read from examples.df929, processed dataframe.  less obfuscation in script.
from examples.df929 import df, chnAttLookup

####2016-10-12 [Evan] Remove columns
removeThese=["agg02","featagg08", "featagg02", u'rank7', u'rank14', u'rank60', u'c28', u'c30', u'c34', u'c45',"positive_comment_num","negative_comment_num","medium_comment_num", "is_in_stock"]
df = df.drop(removeThese, axis=1)

####2016-10-09 [Evan] Normalize columns (optional)
df = rlp.normalizeColumns(df)
df = rlp.flipRankCols(df)

####2016-10-11 [Evan] Add a bin/int tag to columnnames
bincolumns = [col for col in df.columns if len(df[col].unique())<=3 and col!="page"]
df = df.rename(columns={name: name+"bin" for name in bincolumns})
intcolumns = [col for col in df.columns if len(df[col].unique())>3 and col!="page"]
df = df.rename(columns={name: name+"int" for name in intcolumns})


#End Preprocessing step
print "Total rows (M) after preprocessing: %i" % len(df)

#Start Solving Rank LP's

#specify solving method (add more here for whichever methods are installed)
solver=PULP_CBC_CMD()                      #default, comes with pulp
#solver=GLPK()





####2016-10-08 [Evan] Make upper/lower bounds variable
#upperA = 100    ###(default 10)  ###copy this into params: ubound_a=upperA
#upperV = 100    ###(default 100) ###copy this into params: ubound_v=upperV
#lowerA = .001    ###(default .01) ###copy this into params: lbound_a=lowerA
lowerV = 1      ###(default .01) ###copy this into params: lbound_v=lowerV

pageset = {1:range(1,2),
           2:range(2,4),
           3:range(4,8)} 

#### NEED TO ADD: progressbar

threshes = {"bin": (.5,2,8), "int":(.02, .1, 1)}
threshloop = [(a,b) for a in threshes["bin"] for b in threshes["int"]]

###2016-10-12 [Evan] Add the attributes to a list.  Then histogram these!  
### The object will be structured as follows: atts["prod"]["a_c26int"] --> [.8, .76, .54, .. ]
###
### build this into the innermost loop, where the importance dictionary is created. 
atts = {"prod":{}, "page":{}, "pageset":{}}
###
### NOTE: adding this outside of loop so that there are more numbers accumulated tonight


for threshbin,threshint in threshloop:
    # Create value containers
    resultList1 = []
    resultList2 = []
    resultList3 = []
    importanceDictprod = {}
    importanceDictpage = {}
    importanceDictpageset = {}
    

    
    
    # Loop 1000 times and save the results into containers
    maxiter=30
#    thresh =.02
    for i in range(maxiter):
        if i%10==0: print "iteration %i\t(out of %i)" % (i, maxiter)
        prob_page = rlp.forceSolution(df, by="page", solver=solver, lbound_v=lowerV)    
        prob_pageset = rlp.forceSolution(df, by="pageset", solver=solver, c=pageset, lbound_v=lowerV)
        df2 = df.drop("page", axis=1)
        prob_prod = rlp.forceSolution(df2, by="product", solver=solver, lbound_v=lowerV)
        if prob_prod:
            M1 = len([s for s in prob_prod.variables() if s.name.startswith("v_0")])
            resultList1.append(M1)
            for a1 in prob_prod.variables():
                if a1.name.startswith("a_"):
                    if a1.name.endswith("int") and a1.varValue>threshint:
                        importanceDictprod[a1.name]=importanceDictprod.get(a1.name,0) + 1
                    if a1.name.endswith("bin") and a1.varValue>threshbin:
                        importanceDictprod[a1.name]=importanceDictprod.get(a1.name,0) + 1
                    atts["prod"][a1.name] = atts["prod"].get(a1.name,[]) + [a1.varValue]

                    
        if prob_page:
            M2 = len([s for s in prob_page.variables() if s.name.startswith("v_0")])
            resultList2.append(M2)
            for a2 in prob_page.variables():
                if a2.name.startswith("a_"):
                    if a2.name.endswith("int") and a2.varValue>threshint:
                        importanceDictpage[a2.name]=importanceDictpage.get(a2.name,0) + 1
                    if a2.name.endswith("bin") and a2.varValue>threshbin:
                        importanceDictpage[a2.name]=importanceDictpage.get(a2.name,0) + 1
                    atts["page"][a2.name] = atts["page"].get(a2.name,[]) + [a2.varValue]
                    
        if prob_pageset:
            M3 = len([s for s in prob_pageset.variables() if s.name.startswith("v_0")])
            resultList3.append(M3)
            for a3 in prob_pageset.variables():
                if a3.name.startswith("a_"):
                    if a3.name.endswith("int") and a3.varValue>threshint:
                        importanceDictpageset[a3.name]=importanceDictpageset.get(a3.name,0) + 1
                    if a3.name.endswith("bin") and a3.varValue>threshbin:
                        importanceDictpageset[a3.name]=importanceDictpageset.get(a3.name,0) + 1
                    atts["pageset"][a3.name] = atts["pageset"].get(a3.name,[]) + [a3.varValue]


    exectime = "\ntime to execute script: %.1f hours\n" % ((time.time() - scriptStartTime)/3600.)
    print exectime


    ###2016-10-10 Print a sample solution (the last one found)
    rlp.plotSolutions(prob_prod, prob_page, prob_pageset, pageset, lowerV, saveimg=True)


    importanceDict = {"prod":importanceDictprod,"page":importanceDictpage,"pageset":importanceDictpageset}
    M              = {"prod":resultList1,"page":resultList2,"pageset":resultList3}

'''
    # Write the containers(results) into files
    with open("output/product_ms.txt", 'w') as file1:
        for item in resultList1:
            file1.write("{}\n".format(item))


    with open("output/page_ms.txt", 'w') as file2:
        for item in resultList2:
            file2.write("{}\n".format(item))


    with open("output/pageset_ms.txt", 'w') as file3:
        for item in resultList3:
            file3.write("{}\n".format(item))


    with open("output/importanceDict.txt",'w') as file4:
        json.dump(importanceDict, file4)


    ##2016-09-30: add email function
    ##added by email-loving Evan 


    msg = "LP solution script finished!\n\nCounts of solutions for each product type given in bins of [0,2,4,...,68,70]\n"
    msg+= exectime
    msg+= msgtoinclude + "\n\n"
    msg+= str(chnAttLookup) + "\n"
    msg+= "TESTING: binary threshold = %.1f, integer threshold = %.1f \n" % (threshbin,threshint)

    for probtype in ["prod", "page","pageset"]:
        msg += "\nSolutions and important attributes for %s:\n\n" % probtype
        n, bins, plot = plt.hist(M[probtype], range=(0,70), bins=35)
        plt.close()
        msg += str(n)+"\n\n"
        for k in sorted(importanceDict[probtype], key=importanceDict[probtype].get, reverse=True):
            msg += "%s:\t%i\n" % (k,importanceDict[probtype][k])     


    emailEvan(msg)

with open("output/atts.txt",'w') as fh:
    json.dump(atts, fh)
'''
