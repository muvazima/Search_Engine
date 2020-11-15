import os
import glob
import pandas as pd
import re
import string
import itertools
import nltk
import time
from nltk.stem import PorterStemmer
stemming = PorterStemmer()
from nltk.corpus import stopwords
stops = set(stopwords.words("english")) 
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
import pickle
from functools import reduce
from itertools import product
from collections import defaultdict
import json
ps =nltk.PorterStemmer()
from nltk.corpus import stopwords
stops = set(stopwords.words("english")) 
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from numpy import dot
from numpy.linalg import norm

def clean_text(text):
    str1 = " "
    text_lc = "".join([word.lower() for word in text if word not in string.punctuation]) # remove puntuation
    text_rc = re.sub('[0-9]+', '', text_lc)
    tokens = re.split('\W+', text_rc)    # tokenization
    text = [ps.stem(word) for word in tokens if word not in stops]  # remove stopwords and stemming
    return str1.join(text)

def one_word_query_dict(word, invertedIndex,result):
    row_id = []
    final_list = []    
    word = clean_text(word)
    pattern = re.compile('[\W_]+')
    word = pattern.sub(' ',word)
    if word in invertedIndex.keys():
        l = [filename for filename in invertedIndex[word].keys()]
        for filename in l:
            final_list.append(set((invertedIndex[word][filename].keys())))
        
        for i in range(len(l)):
            if l[i] not in result:
                result[l[i]] = final_list[i]
            else:
                result[l[i]] = result[l[i]].union(final_list[i])

def free_text_query(string,invertedIndex):
    string = clean_text(string)
    pattern = re.compile('[\W_]+')
    string = pattern.sub(' ',string)
    result = {}
    for word in string.split():
        one_word_query_dict(word,invertedIndex,result)
    return result

def phrase_query_correct(string,inverted_index):
    string = clean_text(string)
    final_dict = {}
    pattern = re.compile('[\W_]+')
    string = pattern.sub(' ',string)
    listOfDict = []
    for word in string.split():
        result = {}
        one_word_query_dict(word,inverted_index,result)
        listOfDict.append(result.copy())
    common_docs = set.intersection(*map(set, listOfDict))
    words_list = string.split()
    final_res = {}
    for filename in common_docs:
        ts = []
        for word in string.split():
               ts.append(inverted_index[word][filename])
        
        for word_pos_dict_no in range(0,len(ts)):
            for row_number in ts[word_pos_dict_no]:
                for positions in range(0,len(ts[word_pos_dict_no][row_number])):
                    ts[word_pos_dict_no][row_number][positions] -= word_pos_dict_no
        common_rows = set.intersection(*map(set,ts))
        for row_number in common_rows:
            final_list_of_pos = []
            for word_no in range(0,len(ts)):
                final_list_of_pos.append(ts[word_no][row_number])                    
            res = list(reduce(lambda i, j: i & j, (set(x) for x in final_list_of_pos)))
            if(len(res)>0):
                if(filename not in final_res):
                    final_res[filename] = []
                final_res[filename].append(row_number)
    return final_res

def query_vec(query):
    vectorizer = TfidfVectorizer(vocabulary=list(inverted_index.keys()))
    corpus = [query]
    queryVec = vectorizer.fit_transform(corpus)
    return queryVec.toarray()[0]

def doc_vec(document,rowno):
    return documentvectors[document][int(rowno)].toarray()

def printresult(query_type,query): #prints the snippets
        
        start=time.time()
        if(query_type == "1" and len(query) == 1):
            res=one_word_query_dict(query,inverted_index)
        elif(query_type == "1"):
            res=free_text_query(query,inverted_index)
        elif(query_type == "2" ):
            res=phrase_query_correct(query,inverted_index)
        elif(query_type != "1" and query_type != "2" ):
            print("Please enter a valid query type")
            return
        else:
            print("There are no matches for this query")
            return

        sim={}
        query_clean = clean_text(query)
        q_vec= query_vec(query_clean)
        if type(res) == type({}):
            for document,rows in res.items():
                for row in rows:
                    d_vec=doc_vec(document,row)
                    sim[document+','+row] = float(dot(d_vec,q_vec) /(norm(d_vec) * norm(q_vec)))
        elif type(res) == type([]):
            for result in res:
                for document,rows in result.items():
                    for row in rows:
                        d_vec=doc_vec(document,row,query)
                        sim[document+','+row]=(dot(d_vec,q_vec) /(norm(d_vec) * norm(q_vec)),norm(d_vector))

        else:
             pass
        sim_sorted = sorted(sim.items(), key=lambda x: x[1], reverse=True)
        sim_sorted= sim_sorted[0:10]
        for k, v in sim_sorted:
             if v != 0.0:
                print("Similarity value:", v)
                doc,row=k.split(",")
                print("Document Name:",doc)
                infile = f'Dataset/{doc}'
                data = pd.read_csv(infile, skiprows = int(row) , nrows=1, usecols=[6])
                print("Snippet: ",data.values[0][0])
                print("\n\n\n")

        end=time.time()
        print("Execution Time: ",end-start)

def enter_query():
    print("Please input the type of Query : \n '1' for free text queries \n '2' for phrase queries ")
    query_type = input()
    print("Please enter the query")
    query = input()
    printresult(query_type,query)

with open('inverted_index.json') as f:
    inverted_index = json.load(f)

with open('vectorspace.pickle',"rb") as f:
    documentvectors = pickle.load(f)

enter_query()

