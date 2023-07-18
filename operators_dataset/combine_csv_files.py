import numpy as np
import pandas as pd

operators = ['Smartfren','Telkomsel','Tri','XL','Axis','Indosat']
dictionary = {}

dframe_combined = pd.DataFrame()

for operator in operators :
    dictionary["df_{}".format(operator)] = pd.read_csv("{}_Products.csv".format(operator))
    dictionary["df_{}".format(operator)]['Operator'] = str(operator)
    to_combine = dictionary["df_{}".format(operator)]
    dframe_combined = pd.concat([dframe_combined,to_combine],axis=0).reset_index().drop(['index'],axis=1)
print(dframe_combined)

dframe_combined.fillna("0",inplace=True)

for col in dframe_combined.columns:
    dframe_combined[col] = dframe_combined[col].apply(lambda x : np.nan if x == "0" else x )
dframe_combined.to_csv("All_Operators.csv")



