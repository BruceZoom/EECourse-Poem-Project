import pandas as pd

fname = 'guci_dict.txt'

df = pd.read_csv(fname, sep=' ', names=['word', 'freq'], encoding='utf-8')
# print(1.0/(df.loc[:, 'freq']+1))
df.loc[:, 'freq'] = df.loc[:, 'freq'].astype(int) + 1
df.to_csv(fname, sep=' ', header=False, encoding='utf-8', index=False)