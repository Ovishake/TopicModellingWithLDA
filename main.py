#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 21:09:03 2019

@author: ovishake
"""

import pickle as cPickle
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
from operator import itemgetter
import os

stop = set(stopwords.words('english'))
lemma = WordNetLemmatizer()

lda_fp = open("lda_model_sym_wiki.pkl", 'rb')
ldamodel = cPickle.load(lda_fp)

def rem_ascii(s):
    return "".join([c for c in s if ord(c) < 128 ])

def clean_doc(doc):
    doc_ascii = rem_ascii(doc)
    stop_free = " ".join([i for i in doc_ascii.lower().split() if i not in stop])
    normalized = " ".join(lemma.lemmatize(word,'v') for word in stop_free.split())
    x = normalized.split()
    y = [s for s in x if len(s) > 2]
    return y

def get_theme(doc):
    topics = "Electrical_systems_or_Education unknown music unknown Software \
    International_event Literature War_or_Church Lingual_or_Research Biology \
    Waterbody Wikipedia_or_Icehockey unknown unknown html_tags sports TV_shows \
    Terms_and_Services music US_states Timeline Chemistry Germany Location_area \
    Film_awards Games US_school unknown Railways Biography Directions_Australlia \
    France India_Pakistan Canada_politcs_or_WWE Politics unknown British_Royal_Family \
    American_Movies unknown Colors_or_Birds Fauna Chinese_Military unknown unknown \
    unknown unknown unknown html_tags US_Govt Music_band".split()
    
    theme = ""
    cleandoc = clean_doc(doc)
    doc_bow = ldamodel.id2word.doc2bow(cleandoc)
    doc_topics = ldamodel.get_document_topics(doc_bow, minimum_probability=0.20)
    if doc_topics:
        doc_topics.sort(key = itemgetter(1), reverse=True)
        theme = topics[doc_topics[0][0]]
        if theme == "unknown":
            theme = topics[doc_topics[1][0]]
    else:
        theme = "unknown"
    return theme


def get_related_documents(term, top, corpus):
    print ("-------------------",top," top articles related to ",term,"-----------------------")
    clean_docs = [clean_doc(doc) for doc in corpus]
    related_docid = []
    test_term = [ldamodel.id2word.doc2bow(doc) for doc in clean_docs]
    doc_topics = ldamodel.get_document_topics(test_term, minimum_probability=0.20)        
    term_topics =  ldamodel.get_term_topics(term, minimum_probability=0.000001)
    for k,topics in enumerate(doc_topics):
        if topics:
            topics.sort(key = itemgetter(1), reverse=True)
            if topics[0][0] == term_topics[0][0]:
                related_docid.append((k,topics[0][1]))
    
    related_docid.sort(key = itemgetter(1), reverse=True)
    for j,doc_id in enumerate(related_docid):
        print (docs_test[doc_id[0]],"\n",doc_id[1],"\n")   
        if j == (top-1):
            break


def cluster_similar_documents(corpus, dirname):
    clean_docs = [clean_doc(doc) for doc in corpus]
    test_term = [ldamodel.id2word.doc2bow(doc) for doc in clean_docs]
    doc_topics = ldamodel.get_document_topics(test_term, minimum_probability=0.20)    
    for k,topics in enumerate(doc_topics):        
        if topics:
            topics.sort(key = itemgetter(1), reverse=True)
            dir_name = dirname + "/" + str(topics[0][0])           
            file_name = dir_name + "/" + str(k) + ".txt"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)    
            fp = open(file_name,"w")
            fp.write(docs_test[k] + "\n\n" + str(topics[0][1]) )
            fp.close()        
        else:           
            if not os.path.exists(dirname + "/unknown"):
                os.makedirs(dirname + "/unknown")  
            file_name = dirname + "/unknown/" + str(k) + ".txt"
            fp = open(file_name,"w")
            fp.write(docs_test[k]) 

docs_fp = open("docs_wiki.pkl", 'rb')
docs_all = cPickle.load(docs_fp)
docs_test = docs_all[60000:]


get_related_documents("canada",10,docs_test)
cluster_similar_documents(docs_test,"root")
article = "Microsoft's latest update upheaval will have long-term impact on Windows 10,\
        affecting enterprise and small business upgrade scheduling and pushing consumers\
        to continue working as free testers for the company."
print (article, "\n")

print ("Theme -> ",get_theme(article))