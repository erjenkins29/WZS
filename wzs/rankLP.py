
# coding: utf-8

####How to use:
#
###1. Preprocess some pandas df
#
#import rankLP as rlp
#
#catfenlei = 0
#df = rlp.catFenleiFilter(df, catfenlei)
#df = rlp.stringFilter(df)
#df = rlp.zeroVarFilter(df)
#df = rlp.addPage(df)
#df = df.sort_values(by="rank")
#df.index = ["%04i"%i for i in df["rank"]]
#df = df.drop("rank",axis=1)
#
#
###2. Generate the LP Problem and solve
#
#solver=PULP_CBC_CMD()                      #default, comes with pulp
##solver=GLPK()
#
#prob_page = rlp.rankByPage(df)
#prob_page.solve(solver)
#
### Alternatively, a solution can be forced using forceSolution()
#
#prob_page = rlp.forceSolution(df, by="page", solver=solver)
#
###Two important notes:
##  1. if using rankByProduct, make sure to drop the "page" feature
##  2. make sure the input df is sorted by rank.
#
###3. Visualize the results
#
#rlp.viewAs(prob_page)
#rlp.viewBCs(prob_page)
#
#
#Sample data included in script (called inputdf)


import pandas as pd
import numpy as np
from pulp import *
import progressbar as pb
from matplotlib import pyplot as plt

####Preprocessing functions

def catFenleiSorter(df):
    listOfCounts = pd.Series()
    for cat in df.categoryid.unique():
        if np.isnan(cat): continue
        tmp = df.loc[df.categoryid==cat,:].fenlei.value_counts()
        tmp.index = "%i/"%(cat)+tmp.index
        listOfCounts = pd.concat([listOfCounts,tmp])
    return listOfCounts.sort_values(ascending=False)

def catFenleiFilter(df, order=0):
    ## first group all combinations of category/fenlei, then sort them by value_counts().  The 'order'
    ## variable corresponds to this sorted list-- if order=0, then the returned dataframe will be the 
    ## category/fenlei combination with the most values.  order=1 will be the 2nd most, and so on.
    sortedCatFenleis = catFenleiSorter(df)
    key = sortedCatFenleis.index[order]
    category, fenlei = key.split("/")
    category = int(category)
    return df.loc[(df.categoryid==category) & (df.fenlei==fenlei),:]

def removeNArows(df):
    ##need to analyze if this is worth the effort
    
    return

def zeroVarFilter(df):
    removeThese = [col for col in df.columns if len(df[col].unique())==1]
    return df.drop(removeThese, axis=1)

def stringFilter(df, keepThese=['fenlei', 'is_in_stock']):
    removeThese = [col for col in df.columns if df[col].dtype.str=="|O" and col not in keepThese]
    return df.drop(removeThese, axis=1)

def pageNum(rank, pageSize=60):
    ##expecting integer rank
    return (rank-1)/pageSize + 1
    
def addPage(df, rankColName="rank"):
    df["page"] = df[rankColName].astype(int).apply(pageNum)
    return df

###Added (10/9)
###2016-10-10 edited to not normalize the page column

#def normalizeColumns(df):
#    if "page" in df.columns:
#        pagecol = df.page
#    df = df.apply(lambda x: x/max(x))
#    df["page"] = pagecol
# return df
#
### replace with below after test  ###

### added by TX(10/14)
def normalizeColumns(df,normConstant=1,normBinaries=False):
### normConstant is the max number to normalize by;
### normBinaries==False means that binary-valued columns will not be normalized
    if normBinaries==True:
        if "page" in df.columns:
            pagecol = df.page
            df = df.apply(lambda x: normConstant*x/max(x))
            df["page"] = pagecol
        else:
            df = df.apply(lambda x: normConstant*x/max(x))
    else:
        if "page" in df.columns:
            pagecol = df.page
            for colname in df.columns:
                if len(df[colname].fillna(0).unique())<=2: continue
                df[colname] = normConstant*df[colname]/max(df[colname])
            df["page"] = pagecol
        else:
            for colname in df.columns:
                if len(df[colname].fillna(0).unique())<=2: continue
                df[colname] = normConstant*df[colname]/max(df[colname])

    return df


###Added (10/10)
def flipRankCols(df):
    rankcols = [col for col in df.columns if col.startswith("rank")]
    for colname in rankcols:
        df[colname] = max(df[colname]) - df[colname]
    return df

####LP problem solving functions

def rankByProduct(inputdf,
                  lbound_a=0.01,
                  ubound_a=10,
                  lbound_v=0.01,
                  ubound_v=100):
    ###2016-09-28 -Adding lbound, ubound params to function.  Removing returnStatus param
    ###2016-09-28 -Changing objective function to be sum(v_0[i])
    
    problem = LpProblem("find a solution for ranks", LpMinimize)

    nrows, ncols   = inputdf.shape
    cnames, rnames = inputdf.columns, inputdf.index

    a_ = LpVariable.dicts(name="a_", indexs=cnames, lowBound=lbound_a,upBound=ubound_a)
    v_0= LpVariable.dicts(name="v_0", indexs=rnames, lowBound=lbound_v,upBound=ubound_v)
#    problem += lpSum([a_[i] for i in cnames]), "The objective function"
    problem += lpSum([v_0[i] for i in rnames]), "The objective function"

    for i, next_i in zip(rnames[:-1],rnames[1:]):
        problem += lpSum([inputdf.loc[i,j]*a_[j] - v_0[i] for j in cnames]) == 0
        ####START edit
        #REMOVE
        #problem += v_0[i] - v_0[next_i] >= 0
        if   lbound_v <= 0: print "invalid lower bound for v_0: negative number or zero"; return
        else: problem += v_0[i] - v_0[next_i] >= 0
        ####END edit
    problem += lpSum([inputdf.loc[rnames[-1],j]*a_[j] - v_0[rnames[-1]] for j in cnames]) == 0
    
    return problem

    
def rankByPage(inputdf,
               lbound_a=0.01,
               ubound_a=10,
               lbound_v=0.01,
               ubound_v=100):
    ## this function expects a dataframe
    ## with: page column
    ## 
    ## without: rank column

    ###2016-09-28 -adding lbound, ubound params to function.  Removing returnStatus param
    ###2016-09-28 -Changing objective function to be sum(v_[i])
    
    problem = LpProblem("find a solution for ranks", LpMinimize)

    pages = ["%03i" % i for i in inputdf.page.unique()]
    nrows, ncols   = inputdf.shape
    rnames, cnames  = inputdf.index, inputdf.columns.drop("page")
    
    a_ = LpVariable.dicts(name="a_", indexs=cnames, lowBound=lbound_a,upBound=ubound_a)  ## feature parameters
    v_0= LpVariable.dicts(name="v_0", indexs=rnames, lowBound=lbound_v,upBound=ubound_v)     ## the scores for each product
    b_ = LpVariable.dicts(name="b_", indexs=pages[:-1], lowBound=lbound_v,upBound=ubound_v)  ## page boundaries
    
#    problem += lpSum([a_[i] for i in cnames] + [b_[i] for i in pages[:-1]]), "The objective function"
    problem += lpSum([b_[i] for i in pages[:-1]]), "The objective function"
#    problem += lpSum([a_[i] for i in cnames]), "The objective function"
#    problem += lpSum([v_0[i] for i in rnames]), "The objective function"


    for i in rnames:
        problem += lpSum([inputdf.loc[i,j]*a_[j] - v_0[i] for j in cnames]) == 0, "row %s's value"%i
    
    for pg, next_pg in zip(pages[:-1], pages[1:]):
        rnames_pg      = inputdf[inputdf.page==int(pg)].index
        rnames_next_pg = inputdf[inputdf.page==int(next_pg)].index
        for pg_i in rnames_pg:
            problem += v_0[pg_i] - b_[pg] >= 0
        for next_pg_i in rnames_next_pg:
            problem += b_[pg] - v_0[next_pg_i] >= 0

    for k, next_k in zip(pages[:-2], pages[1:-1]):
        ####START edit
        #REMOVE
        #problem += b_[k] - b_[next_k] >= 0
        if   lbound_v < 0: print "invalid lower bound for v_0: negative number"; return
        else: problem += b_[k] - b_[next_k] >= 0
        ####END edit

    return problem


def rankByPageSet(inputdf,
                  lbound_a=0.01,
                  ubound_a=10,
                  lbound_v=0.01,
                  ubound_v=100,
                  c = {1: [1],          #define the page sets of interest.
                       2: [2,3],
                       3: [4,5,6,7]}):

    ###2016-09-28 -adding lbound, ubound params to function.  Removing returnStatus param
    ###2016-09-28 -Changing objective function to be sum(v_0_[i])
        
    problem = LpProblem("find a solution for ranks", LpMinimize)

    #pages = ["%03i" % i for i in inputdf.page.unique()]
    numOfPageSets = len(c.keys())+1

    ###first create modified c so that it includes all pages that the input dataframe has
    max_pg = 0
    cFiltered = {}
    for k, vv in sorted(c.items()):
        valid_pg = []
        for pg in vv:
            if sum(inputdf.page==pg)>0: valid_pg.append(pg)
            if pg>max_pg: max_pg = pg
        if valid_pg==[]: continue
        cFiltered[k] = valid_pg
        
    ###above only covers the pages defined in the c dictionary.  for the last pageset, iterate over the remaining pages
    cFiltered[numOfPageSets] = inputdf[inputdf.page > max_pg].sort_values(by="page").page.unique().astype(int).tolist()

    pageset = cFiltered.keys()
        
    nrows, ncols   = inputdf.shape
    rnames, cnames  = inputdf.index, inputdf.columns.drop("page")

    a_ = LpVariable.dicts(name="a_", indexs=cnames, lowBound=lbound_a,upBound=ubound_a)  ## feature parameters
    v_0= LpVariable.dicts(name="v_0", indexs=rnames, lowBound=lbound_v,upBound=ubound_v)     ## the scores for each product
    c_ = LpVariable.dicts(name="c_", indexs=pageset[:-1], lowBound=lbound_v,upBound=ubound_v)  ## pageSet boundaries

    #problem += lpSum([a_[i] for i in cnames]), "The objective function"
    #problem += lpSum([v_0[i] for i in rnames]), "The objective function"
    problem += lpSum([c_[i] for i in pageset[:-1]]), "The objective function"
    
    for i in rnames:
        problem += lpSum([inputdf.loc[i,j]*a_[j] - v_0[i] for j in cnames]) == 0, "row %s's value"%i
    
    for (pgset, v), (next_pgset, next_v) in zip(sorted(cFiltered.items())[:-1],sorted(cFiltered.items())[1:]):
        rnames_pg, rnames_next_pg = [],[]
        
        for pg in v:
            rnames_pg      += inputdf[inputdf.page==pg].index.tolist()
        for next_pg in next_v:
            rnames_next_pg += inputdf[inputdf.page==next_pg].index.tolist()
        
        for pg_i in rnames_pg:
            problem += v_0[pg_i] - c_[pgset] >= 0
        for next_pg_i in rnames_next_pg:
            problem += c_[pgset] - v_0[next_pg_i] >= 0

    for k, next_k in zip(pageset[:-2], pageset[1:-1]):
        ####START edit
        #REMOVE
        #problem += c_[k] - c_[next_k] >= 0
        if   lbound_v < 0: print "invalid lower bound for v_0: negative number"; return
        else: problem += c_[k] - c_[next_k] >= 0
        ####END edit
        
        
    return problem
    
    
def forceSolution(df, 
                  by="product",             # can be either "product" or "page"
                  stopHere=5,               # stop iterating once there are this many rows
                  solver=PULP_CBC_CMD(),    # only have PULP_CBC_CMD() and GLPK() available as of 9/25/2016
                  c=None,
                  **kwargs):
    ###2016-09-28 - Add **kwargs to allow for changing the ubounds/lbounds/strict conditions
    
    if by=="product":
        for i in range(len(df),1,-1):
            prob   = rankByProduct(df.sample(i).sort_index(), **kwargs)
            status = prob.solve(solver)
            if status==1: return prob
            if i==stopHere: print "No solutions found"; return
    if by=="page":
        for i in range(len(df),1,-1):
            prob   = rankByPage(df.sample(i).sort_index(), **kwargs)
            status = prob.solve(solver)
            if status==1: return prob
            if i==stopHere: print "No solutions found"; return
    if by=="pageset":
        for i in range(len(df),1,-1):
            if c is None: prob   = rankByPageSet(df.sample(i).sort_index(), **kwargs)
            else:         prob   = rankByPageSet(df.sample(i).sort_index(),c=c, **kwargs)
            status = prob.solve(solver)
            if status==1: return prob
            if i==stopHere: print "No solutions found"; return


#### Visualization functions
            
def viewAll(prob):
    for i in prob.variables():
        print i.name, "\t=", i.varValue

###2016-10-10 modified to include threshold
def viewAs(prob, thresh=None):
    if thresh is None:
        for i in prob.variables():
            if i.name.startswith("a_"): print i.name, "\t=", i.varValue
    else:
        for i in prob.variables():
            if i.name.startswith("a_") and i.varValue>=thresh: print i.name, "\t=", i.varValue

def viewVs(prob):
    for i in prob.variables():
        if i.name.startswith("v_"): print i.name, "\t=", i.varValue

def viewBCs(prob):
    for i in prob.variables():
        if i.name.startswith(("b_","c_")): print i.name, "\t=", i.varValue
        
def plotSolutions(prob_prod, prob_page, prob_pageset, pageset, lbound_v=0, saveimg=False):
    plt.figure(figsize=(15,5))
    plt.style.use("seaborn-darkgrid")
    
    plt.subplot(131)
    plotme = pd.DataFrame([(int(s.name[4:]), s.varValue) for s in prob_prod.variables() if s.name.startswith("v_0")], columns=["rank0","score"])
    plt.scatter(plotme.rank0, plotme.score, s=5)
    plt.plot(plotme.rank0, plotme.score, "g-", linewidth=2)
    plt.xlim(0);plt.ylim(lbound_v)
    plt.ylabel("$score \ = \  ( \sum a_ix_i )$");plt.xlabel("item_rank") 
    #xticks([i for i in plotme.rank0 if plotme.rank0.tolist().index(i)%7==0]+[plotme.rank0.max()]); 
    #yticks([1]); 
    plt.title("product\n$p_1 \geq p_2 \geq \dots \geq p_M$\nM=%i"%len(plotme))

    def makeBoundSquare(xupper,xlower,yupper,ylower, color="r"):
        plt.plot([xlower, xlower, xupper, xupper, xlower], [yupper, ylower, ylower, yupper, yupper], color=color, linewidth=2)
    
    plt.subplot(132)
    plotme = pd.DataFrame([(int(s.name[4:]), s.varValue) for s in prob_page.variables() if s.name.startswith("v_0")], columns=["rank0","score"])
    plt.scatter(plotme.rank0, plotme.score, s=5)
    #plot(plotme.rank0, plotme.score, alpha=0.3)
    pageBounds = pd.DataFrame([(int(b.name[3:]), b.varValue) for b in prob_page.variables() if b.name.startswith("b_")],columns=["page","lowerBound"])
    pageBounds["lastRankedItem"] = pageBounds.page * 60
    ybounds = [plotme.score.max()] + pageBounds.lowerBound.tolist() + [1]
    xbounds = [0] + pageBounds.lastRankedItem.tolist() + [plotme.rank0.max()]
    for x1,x0,y1,y0 in zip(xbounds[1:],xbounds[:-1],ybounds[:-1],ybounds[1:]):
        makeBoundSquare(x1,x0,y1,y0)
    plt.xlim(0);plt.ylim(lbound_v);plt.xlabel("item_rank"); 
    #xticks([i for i in xbounds if xbounds.index(i)%3==1]); 
    #yticks([1]); 
    plt.title("page\n$\\beta_1 \geq \\beta_2 \geq \dots \geq \\beta_P$\nM=%i"%len(plotme))

    plt.subplot(133)
    plotme = pd.DataFrame([(int(s.name[4:]), s.varValue) for s in prob_pageset.variables() if s.name.startswith("v_0")], columns=["rank0","score"])
    plt.scatter(plotme.rank0, plotme.score, s=5)
    #plot(plotme.rank0, plotme.score, alpha=0.3)
    pageBounds = pd.DataFrame([(int(c.name[3:]), c.varValue) for c in prob_pageset.variables() if c.name.startswith("c_")],columns=["pageset","lowerBound"])
    pageBounds["lastRankedItem"] = [60*pageset[i][-1] for i in pageBounds.pageset]
    ybounds = [plotme.score.max()] + pageBounds.lowerBound.tolist() + [1]
    xbounds = [0] + pageBounds.lastRankedItem.tolist() + [plotme.rank0.max()]
    for x1,x0,y1,y0 in zip(xbounds[1:],xbounds[:-1],ybounds[:-1],ybounds[1:]):
        makeBoundSquare(x1,x0,y1,y0,color="purple")
    plt.xlim(-20);plt.ylim(lbound_v);plt.xlabel("item_rank"); 
    #xticks(xbounds[1:]); 
    #yticks([1]); 
    titlestring = "pageset\n$"
    for i in range(len(pageBounds)):
        titlestring += "\Psi_%i\geq" %(i+1)
    titlestring += "\Psi_%i$\nM=%i"%(len(pageBounds)+1,len(plotme))
    plt.title(titlestring)
    plt.tight_layout()
    if saveimg: plt.savefig("images/solution_example.png")
        
###Remove?####
###
def lookAround(inputdf,
               nrowsToRemove=1):
    
    prob, status = rankByProduct(inputdf, returnStatus=True)
    if status > 0:       print "Found solution without removing rows!"; return prob
    if nrowsToRemove==0: print "No solutions found"; return
    
    rnames = inputdf.index
    N = len(rnames)
    
    print "Searching by removing 1 row at a time (%i iterations)..." % N
    bar = pb.ProgressBar(maxval=N, widgets=[pb.Bar("=","[","]"), " ",pb.Percentage()])

    bar.start()
    for i in rnames:
        prob, status = rankByProduct(inputdf.drop(i), returnStatus=True)
        #print "Removing row %s, status = %i"%(i,status)
        if status > 0: 
            bar.finish()
            print "Found solution after removing row %s, status=%i" %(i,status)
            return prob
        bar.update(int(i))
    bar.finish()
    
    if nrowsToRemove==1: print "No solutions found"; return
    
    print "Searching by removing 2 rows at a time (%i iterations)..." % (N*(N-1)/2)
    bar2 = pb.ProgressBar(maxval=N*(N-1)/2, widgets=[pb.Bar("=","[","]"), " ",pb.Percentage()])

    bar2.start()
    k=0
    for name1, i in zip(rnames[:-1], range(len(rnames)-1)):
        for name2 in rnames[i+1:]:
            prob, status = rankByProduct(inputdf.drop([name1,name2]), returnStatus=True)
#            print "Removing rows %s, %s, status = %i"%(name1,name2,status)
            if status > 0: 
                bar2.finish() 
                print "Found solution after removing rows %s,%s out of %i rows\nstatus=%i" %(name1,name2,len(rnames),status)
                return prob
            k+=1
            bar2.update(k)
    bar2.finish()
    
    if nrowsToRemove==2: print "No solutions found"; return
###
###
