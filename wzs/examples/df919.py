import pandas as pd

## Sample data
df = pd.read_excel("/data/merged0919withq30.xls",index_col="egoodsid")
#for i in range(8):
#    print "\nfenlei index %i:\n" %i, df.loc[df.fenlei==df.fenlei.value_counts().index[i],:].categoryid.value_counts()

columns_to_drop = ["brandtag", "goodsid", 
                   "ecatid", #"categoryid",  #Don't drop yet
                   "goodsname", "goodsattribute", 
                   "updatetime", "promotioninfo", 
                   "crawlerdate", #"fenlei",   #Don't drop fenlei yet.  You'll need to filter the rows first, then drop 
                   "is_promo", # removing, since no variance in the column at fenlei level
                   "agg1", # removing, since no variance in the column at fenlei level
                   "agg2", # removing, since no variance in the column at fenlei level
                   "agg3", # removing, since no variance in the column at fenlei level
                   "agg4", # removing, since no variance in the column at fenlei level
                   "agg5", # removing, since no variance in the column at fenlei level
                   "agg7", # removing, since no variance in the column at fenlei level
                   "agg8", # removing, since no variance in the column at fenlei level
                   "goodsstatus", # removing, since no variance in the column at fenlei level
                   "platform_brand_key", # removing, since no variance in the column at fenlei level
                   "master_brand_key", "goods_inventory",
                   "c1", "allcommentschange"]
df = df.drop(columns_to_drop, axis=1)

df = df.loc[(df.c26.notnull()) & (df.rank60.notnull()) & (df.rank7.notnull()) & (df.index.value_counts(dropna=False)<2) & (df.allcomments.notnull()),:]

category_to_analyze = 0
fenlei_to_analyze = 5
df = df.loc[df.fenlei == df.fenlei.value_counts().index[fenlei_to_analyze],:]
df = df.loc[df.categoryid == df.categoryid.value_counts().index[category_to_analyze],:]
df = df.drop(["categoryid","fenlei"], axis=1)
df = df.fillna(0).sort_values(by="rank")
df.index = ["%02i" % (i+1) for i in range(len(df))]
df = df.drop("rank", axis=1)
