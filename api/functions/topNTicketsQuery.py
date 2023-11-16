#Get Top N Ticket by query

import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, text
import ast
import numpy as np
from flask import jsonify
import json

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.test.utils import get_tmpfile

def getTopNSimilarTicketsByQuery (text,n):
    
    n = int(n)
    
    username = 'root'
    password = ''
    host = 'localhost'
    database = 'itaca'
    engine = ''
    metadata = ''
    
    '''
    Carica il modello 
    '''
    
    epochs = 30
    vectorsize = 200
    fname = "models/my_doc2vec_model_epochs_"+str(epochs)+"_d"+str(vectorsize)
    #Load model from disk
    
    model = Doc2Vec.load(fname)  # you can continue
    
    print("Preprocessa")
    
    import functions.spacyTokenizer as st
    textTokens = st.preprocessTextSpacy(text)
    print("Codifica in forma vettoriale")
    # Crea il vettore del nuovo ticket usando il modello addeestrato
    textVector = model.infer_vector(textTokens)
    
    '''
    Cerca tutti i tickets che hanno in comune almeno un token
    '''
    print(textTokens)
    print(type(textTokens[0]))
    otherTickets = ''
    try:
        engine = create_engine(f"mysql+mysqldb://{username}:{password}@{host}/{database}")
        metadata = MetaData()
        # Esegui la query SELECT e inserisci il risultato in un DataFrame
        where = ' 1!=1 '
        for token in textTokens:
            where += " OR tokens2 LIKE '%" + token+ "%' "
            
        #query = "SELECT * FROM nlp WHERE " + where
        query = "SELECT * FROM nlp"
        print(query)
        #res = pd.read_sql(text(query), con=engine)
        res = pd.read_sql(query, con=engine)
        res['tickets2'] = res['tokens2'].apply(ast.literal_eval)
        res['vector'] = res['vector'].apply(lambda x:(np.fromstring(x.lstrip("[").rstrip("]"), dtype=float, sep=' ')))
        otherTickets = res
    except Exception as e:
        print("qui")
        print("errore")
        print(e) 
        return str(e)
        
        
    print(otherTickets)
    print("ok")
    
    '''
    Confronta il ticket con gli altri che hanno in comune almeno un token calcolandone per
     ciascuno la similarità, e poi restituisce gli n tickets più simili.
    '''
    idx_lookup_vector = {otherTickets['idprobl'][idx] : np.fromstring(vector) for idx, vector in enumerate(otherTickets['vector'])}

    def similarity(x, y):
        #x = model.infer_vector(preprocessTextSpacy(text1))
        #y = model.infer_vector(preprocessTextSpacy(text2))
        cos_sim =  np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))
        return cos_sim

    #Funzione Alternativa di recupero 10 ticket più simili
    
    #text = "Avendo due installazioni identiche (con una sola chiave hd) posso lavorare su uno solo e ripristinare sull'altro"
    #testo_da_confrontare = model.infer_vector(preprocessTextSpacy(text))
    similarity_score = [[ idx, similarity(textVector, idx_lookup_vector[idx])] for idx in idx_lookup_vector.keys() ]
    sorted_list = sorted(similarity_score, key=lambda x: x[1], reverse=True)
    print(type(sorted_list))
    top_n_tickets=sorted_list[1:n+1]
    print(top_n_tickets)
    
    mostSimilar = []
    for item in top_n_tickets:
        currentTicket = otherTickets[otherTickets['idprobl'] == item[0]].drop(columns=['vector'])
        currentTicket['_similarity'] = item[1]
        mostSimilar.append(json.loads(currentTicket.to_json(orient='records')))
        
    output = { 'text_query': text, 'most_similar': mostSimilar }
    
    return jsonify(output)