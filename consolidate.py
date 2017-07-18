import sys

#consolidate.py outfile [infile1,infile2,...]
try:
    out_file = sys.argv[1]
except IndexError:
    print("must specify out file")

file_list = sys.argv[1:]

for f in file_list:
    with open(f,'r') as fp:
        reader = csv.read(fp)
