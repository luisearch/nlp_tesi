#Get Top N Ticket by aaprobl and nnprob

import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, text
import ast
import numpy as np
from flask import jsonify
import json

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.test.utils import get_tmpfile

def codifyNewTicket (aaprobl,nroprobl,desprobl):
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
    vectorsize = 50
    fname = "models/my_doc2vec_model_epochs_"+str(epochs)+"_d"+str(vectorsize)
    #Load model from disk
    
    model = Doc2Vec.load(fname)  # you can continue
    
    '''
     [SOLO PER TEST] Crea un nuovo ticket e lo inserisce come nuova riga nella tabella itpbc (DI QUESTO COMPITO SE NE OCCUPA UN SERVIZIO ESTERNO, MA SIMULIAMO IN QUESTA FASE LA CREAZIONE DEL NUOVO TICKET)
    '''
    try:
        engine = create_engine(f"mysql+mysqldb://{username}:{password}@{host}/{database}")
        metadata = MetaData()
        
        with engine.connect() as conn:
            result = conn.execute(text("INSERT INTO itpbc (aaprobl, nroprobl, codcli, codcliu, codtyrich, datarich, hhrich, dessinprobl, desprobl, swrisol, swgett) VALUES ('"+aaprobl+"', '"+nroprobl+"', '     1', '1', 'INFO', '2023-10-07', '09:13:05', 'Questo è un test (ignorare)', '" + desprobl + "', 'N', 'N');"))
            conn.commit()
    except Exception as e:
        print("errore")
        print(str(e)) #problema in fase di creazione nuovi campi della tabella itaca.itpbc
        return str(e)
    
    '''
     Preprocessa e codifica il nuovo ticket e inserisce una nuova riga
    '''
    print("Preprocessa")
    
    import functions.spacyTokenizer as st
    ticketTokens = st.preprocessTextSpacy(desprobl)
    
    print("Codifica in forma vettoriale")
    # Crea il vettore del nuovo ticket usando il modello addeestrato
    ticketVector = model.infer_vector(ticketTokens)
    
    try:
        engine = create_engine(f"mysql+mysqldb://{username}:{password}@{host}/{database}")
        metadata = MetaData()
        
        with engine.connect() as conn:
            result = conn.execute(text("INSERT INTO nlp (aaprobl, nroprobl, desprobl, tokens2, vector, idprobl) VALUES ('"+aaprobl+"', '"+nroprobl+"', '" + desprobl + "', \""+str(ticketTokens)+"\", \""+str(ticketVector)+"\",'"+aaprobl+nroprobl+"');"))
            conn.commit()
    except Exception as e:
        print("errore")
        print(str(e)) #problema in fase di creazione nuovi campi della tabella itaca.itpbc
        return str(e)

    output = { 'idprobl':aaprobl+nroprobl,'desprobl': desprobl,'tokens': ticketTokens, 'vector': str(ticketVector)}
    
    return jsonify(output)