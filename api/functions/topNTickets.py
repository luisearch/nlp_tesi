#Get Top N Ticket by aaprobl and nnprob

import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, text
import ast
import numpy as np
from flask import jsonify
import json

def getTopNSimilarTickets (aaprobl,nroprobl,n):
    
    n = int(n)

    username = 'root'
    password = ''
    host = 'localhost'
    database = 'itaca'
    engine = ''
    metadata = ''
    
    tableName = 'nlp_vectors_epochs_1_d200'
    
    ticketData =''
    try:
        engine = create_engine(f"mysql+mysqldb://{username}:{password}@{host}/{database}")
        metadata = MetaData()
        # Esegui la query SELECT e inserisci il risultato in un DataFrame
        query = "SELECT *  FROM "+tableName+" WHERE aaprobl = " +aaprobl + " and nroprobl="+nroprobl
        res = pd.read_sql(query, con=engine)
        res['tokens'] = res['tokens'].apply(ast.literal_eval)
        res['vector'] = res['vector'].apply(lambda x:(np.fromstring(x.lstrip("[").rstrip("]"), dtype=float, sep=' ')))
        ticketData=res.head(1)
        
    except Exception as e:
        print("errore")
        print(str(e)) #problema in fase di creazione nuovi campi della tabella itaca.itpbc
        return str(e)
      
    ticketVector = ticketData['vector'][0]
    ticketTokens = ticketData['tokens'][0]
    print("ok")
    '''
    Cerca tutti i tickets che hanno in comune almeno un token
    '''
    print(ticketTokens)
    print(type(ticketTokens))
    otherTickets = ''
    try:
        engine = create_engine(f"mysql+mysqldb://{username}:{password}@{host}/{database}")
        metadata = MetaData()
        # Esegui la query SELECT e inserisci il risultato in un DataFrame
        where = ' 1!=1 '
        for token in ticketTokens:
            where += " OR tokens LIKE '%" + token + "%'"
        query = "SELECT *  FROM  "+tableName+"  WHERE " + where
        res = pd.read_sql(text(query), con=engine)
        res['tickets2'] = res['tokens'].apply(ast.literal_eval)
        res['vector'] = res['vector'].apply(lambda x:(np.fromstring(x.lstrip("[").rstrip("]"), dtype=float, sep=' ')))
        otherTickets = res
    except Exception as e:
        print("errore")
        print(str(e)) #problema in fase di creazione nuovi campi della tabella itaca.itpbc
        return str(e)
    
    print("ok")
    print(ticketData['vector'][0])
    print(type(ticketData['vector'][0]))
    
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
    similarity_score = [[ idx, similarity(ticketVector, idx_lookup_vector[idx])] for idx in idx_lookup_vector.keys() ]
    sorted_list = sorted(similarity_score, key=lambda x: x[1], reverse=True)
    top_n_tickets=sorted_list[1:n+1]
    print(top_n_tickets)
    
    mostSimilar = []
    for item in top_n_tickets:
        currentTicket = otherTickets[otherTickets['idprobl'] == item[0]].drop(columns=['vector'])
        currentTicket['_similarity'] = item[1]
        mostSimilar.append(json.loads(currentTicket.to_json(orient='records')))
        
    mainTicket = json.loads(ticketData.drop(columns=['vector']).to_json(orient='records'))
    output = { 'main_ticket': mainTicket, 'most_similar': mostSimilar }
    
    return jsonify(output)