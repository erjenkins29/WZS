import pandas as pd
import sys

sys.path.append('..')

import wzs.rankLP as rlp

df = pd.read_csv("data/merged0922.csv",index_col="egoodsid",encoding='gbk')

catfenlei = 0
df = rlp.catFenleiFilter(df, catfenlei)
print "category [%s] fenlei [%s]\nTotal rows (M) before preprocessing: %i" %(df.categoryid.unique()[0],df.fenlei.unique()[0],len(df)) 

##rename agg columns to be more sort-friendly
df.rename(columns={a: "agg" + "%02i"%int(a[3:]) for a in df.columns if a.startswith("agg")})

###custom filters
removeThese = ["JD_Code","platform_brand_key", "rating_score"]
df.loc[df["is_in_stock"]=="True","is_in_stock"] = 1
df.loc[df["is_in_stock"]=="False","is_in_stock"] = 0
df["is_in_stock"] = df["is_in_stock"].astype(int)
df = df.drop(removeThese,axis=1)

###standard filters
df = rlp.stringFilter(df)
df = rlp.zeroVarFilter(df)
#df = df.drop([col for col in df.columns if col.find("agg")>=0], axis=1)

###remove rows with zeros (e.g. allcomments==0)
searchThese = [col for col in df.columns if not col.find("agg")>=0 and len(df[col].value_counts())!=2]
df = df[(df[searchThese]==0).sum(axis=1)==0]

###add page number column
df = rlp.addPage(df)

###sort by rank, reindex
df = df.sort_values(by="rank")
df.index = ["%04i"%i for i in df["rank"]]
df = df.drop("rank",axis=1)
