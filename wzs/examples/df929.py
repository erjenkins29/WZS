import pandas as pd
import sys
import re
from scipy.stats import bernoulli

sys.path.append('..')

import wzs.rankLP as rlp

df = pd.read_csv("data/merged0929.csv",index_col="egoodsid",encoding='gbk')

catfenlei = 0
df = rlp.catFenleiFilter(df, catfenlei)
print "category [%s] fenlei [%s]\nTotal rows (M) before preprocessing: %i" %(df.categoryid.unique()[0],df.fenlei.unique()[0],len(df)) 

##rename agg columns to be more sort-friendly
df = df.rename(columns={a: "agg" + "%02i"%int(a[3:]) for a in df.columns if a.startswith("agg")})

###custom filters
removeThese = ["JD_Code","platform_brand_key", "rating_score"]
df.loc[df["is_in_stock"]=="TRUE","is_in_stock"] = 1
df.loc[df["is_in_stock"]=="FALSE","is_in_stock"] = 0
df["is_in_stock"] = df["is_in_stock"].astype(int)
df = df.drop(removeThese,axis=1)

###standard filters
df = rlp.stringFilter(df)
df = rlp.zeroVarFilter(df)
#df = df.drop([col for col in df.columns if col.find("agg")>=0], axis=1)

###remove rows with zeros (e.g. allcomments==0)
searchThese = [col for col in df.columns if not col.find("agg")>=0 and len(df[col].value_counts())!=2]
df = df[(df[searchThese]==0).sum(axis=1)==0]

#apply zeroVarFilter again, to account for columns which became zerovariance after above rows were removed (added 10/9)
df = rlp.zeroVarFilter(df)

####rename chinese characters (added 9/29)
### if column-names have chinese characters, change them into hasAttr%02i
### (added 10/11) hasAttr%02i can be found in dictionary chnAttLookup
chineseCols = [col for col in df.columns if len(re.findall(ur'[\u4e00-\u9fff]+',col))>0]
chnAttLookup= {"hasAttr%02i" % chineseCols.index(i) : i for i in chineseCols}
df=df.rename(columns={v : k for (k,v) in chnAttLookup.items()})

###(added 10/11) add two dummy columns
df["dummy1"]=bernoulli.rvs(.25,0,len(df))
df["dummy2"]=bernoulli.rvs(.85,0,len(df))

###add page number column
df = rlp.addPage(df)

###sort by rank, reindex
df = df.sort_values(by="rank")
df.index = ["%04i"%i for i in df["rank"]]
df = df.drop("rank",axis=1)
