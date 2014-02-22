import re

f = open("xtester.txt")
lines = f.readlines()
f.close()

'''
f = open("tester.txt")
all = f.read()
f.close()
'''

codes = []
comments = []
in_code = True
for n,line in enumerate(lines):
    if "/*" in line: 
        in_code = False
        comments.append([])
        continue
    if "*/" in line: 
        in_code = True
        codes.append([])
        continue
    
    if in_code: codes[-1].append(line)
    else: comments[-1].append(line)
    
#print comments
#print codes
test = zip(comments, codes)
print len(test[0][0])
print len(comments), len(codes)