import pandas as pd

def CreateSUMS(csv):
    df=pd.read_csv(csv)
    df.dropna(inplace=True)
    print(df.head())
    newfile=df.to_csv()
    return newfile