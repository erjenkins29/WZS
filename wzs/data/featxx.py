###added in 2016-10-11
import pandas as pd
import re


def feat_tran(df):
    feat_dic={}
    reg=re.compile(r'feat\d{2}')
    ColumnNames=reg.findall(','.join(df.columns))
    data_lst=[]
    for i in range(len(ColumnNames)):
        dt=df[ColumnNames[i]].copy()
        dt2=dt.str.split(':',1,True).dropna()
        data_lst.append(dt2)
    str_col=','.join(ColumnNames)
    KeyNames=re.findall(r'\d+\d*',str_col) #only find numbers
    for j in range(len(KeyNames)):
        feat_dic[KeyNames[j]]={data_lst[j][0][1]:list(data_lst[j][1])} 
    return feat_dic

feat_ = feat_tran(pd.read_csv("/opt/jupyter/Early Data/WZS/data/merged0929.csv",encoding='GBK'))