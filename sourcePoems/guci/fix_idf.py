with open('guci_idf.txt', 'r', encoding='utf-8') as fin:
   res =  [line for line in fin.readlines() if len(line.split(' ')) == 2]

with open('guci_idf.txt', 'w', encoding='utf-8') as fout:
    fout.writelines(res)
