import csv
import numpy as np
import pandas as pd
import sys
from tabulate import tabulate
import pprint
from itertools import product
import operator

class Query:
    def csv_maker(self,csvf):
        with open(csvf) as csv_file:
            csv_reader = csv.reader(csv_file,delimiter = ",")
            data = []
            for row in csv_reader:
                data.append(row)
            col = data[0]
            a = tabulate(data, headers='firstrow')
            return data

    def select(self,q,col,data):
        if q == '*':
            df = pd.DataFrame(data,columns = col)
            print("SELECT")
            print(df)
            print()
            return col,np.array(data).T.tolist()
        res = []
        c = []
        for i in range(len(q)):
            for j in range(len(col)):
                if(q[i][-1]==col[j]):
                    c.append(q[i][-1])
                    res.append([a[j] for a in data])
        
        df = pd.DataFrame(np.transpose(res),columns = c)
        print("SELECT")
        print(df)
        print()
        return c,res
    
    def where(self,q,col,data):
        d = {'>':operator.gt ,'<':operator.lt,"=":operator.eq,"<=":operator.le,">=":operator.ge}
        a = d[q[1]]
        fil = lambda r: a(r[col.index(q[0])],q[2])
        res = [b for b in np.array(data).T.tolist() if fil(b)]
        
        df = pd.DataFrame(res,columns=col)
        print("WHERE")
        print(df)
        print()
        return col,res
    
    def order(self,q,col,data):
        if(len(q)>1):
            for i in range(len(col)):
                if(col[i] == q[0]):
                    if(q[1].lower()[:4] == 'desc'):
                        data = sorted(data,key=lambda l:l[i],reverse=True)
                    else:
                        data =sorted(data,key=lambda l:l[i])
        else:
            for i in range(len(col)):
                if(col[i] == q[0]):
                    data =sorted(data,key=lambda l:l[i])
        
        df = pd.DataFrame(data,columns = col)
        print("ORDER BY")
        print(df)
        print()
        return

    def join(self,f1,f2,ty):
        if ty == "natural":
            a,b = self.natural(f1,f2)
        else:
            a,b = self.cartesian(f1,f2)
        return a,b
        
    def cartesian(self,f1,f2):
        t1atts = tuple(f1[0])
        t2atts = tuple(f2[0])
        t1tuples = tuple(f1[1:])
        t2tuples = tuple(f2[1:])
        t1columns = set(t1atts)
        t2columns = set(t2atts)
        t1map = {k: i for i, k in enumerate(t1atts)}
        t2map = {k: i for i, k in enumerate(t2atts)}

        def solve(l1, l2):
            return list(product(l1, l2))

        join_on = t1columns & t2columns
        diff = t2columns - join_on
        col_names = list(t1atts + tuple(diff))

        results = []
        for t1row in t1tuples:
            for t2row in t2tuples:
                if solve(t1row, t2row):
                    row = t1row[:]
                    for rn in diff:
                        row.append(t2row[t2map[rn]])
                    results.append(row)
        return col_names,results

    def natural(self,f1,f2):
        t1atts = tuple(f1[0])
        t2atts = tuple(f2[0])
        t1tuples = tuple(f1[1:])
        t2tuples = tuple(f2[1:])
        t1columns = set(t1atts)
        t2columns = set(t2atts)
        t1map = {k: i for i, k in enumerate(t1atts)}
        t2map = {k: i for i, k in enumerate(t2atts)}

        join_on = t1columns & t2columns
        diff = t2columns - join_on

        def match(row1, row2):
            return all(row1[t1map[rn]] == row2[t2map[rn]] for rn in join_on)

        col_names = list(t1atts + tuple(diff))
        results = []
        for t1row in t1tuples:
            for t2row in t2tuples:
                if match(t1row, t2row):
                    row = t1row[:]
                    for rn in diff:
                        row.append(t2row[t2map[rn]])
                    results.append(row)
        print(results)
        return col_names,results

        query = input("Enter the query : ").split()
print(query)
Q = Query()

if(query[0].lower()=='select' and query[2].lower()=="from"):
    for i in range(len(query)):
        if(query[i].lower()=='from'):
            j = i+1
            while(((query[j].lower()=="natural" or query[j].lower()=="cartesian")and query[j+1].lower()=='join')and (query[j].lower()!="where" or query[j].lower()!="order") and (j<len(query))):
                col_names,data = Q.join(Q.csv_maker(query[j-1]),Q.csv_maker(query[j+2]),query[j].lower())
                j=j+3
            else:
                c = Q.csv_maker(query[i+1])
                col_names,data = c[0],c[1:]

            if(query[i-1] == '*'):
                q = '*'
                b,d = Q.select(q,col_names,data)
        
            else:
                q = list(query[i-1].split(","))
                b,d = Q.select(q,col_names,data)
                

        if(query[i].lower()=='where'):
            col,dat = b,d
            j = i+1
            q = []
            while((j<len(query)) and (query[j].lower()!="order")):
                q.append(query[j])
                j=j+1
            b,d = Q.where(q,col,dat)

        if(query[i].lower()=='order' and query[i+1].lower()=='by'):
            col,dat = b,d
            j = i+2
            o = []
            while((j<len(query))):
                o.append(query[j])
                j=j+1
            Q.order(o,col,dat)
else:
    print("Invalid query")