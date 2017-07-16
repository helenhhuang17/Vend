import csv

with open("product-export.csv",mode='r',encoding='latin-1') as fp:
    reader = csv.reader(fp)
    d = {row[0]:row[6] for row in reader}
