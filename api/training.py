
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, text
import time

from datetime import datetime


# Crea una connessione utilizzando SQLAlchemy 
username = 'root'
password = ''
host = 'localhost'
database = 'itaca'

engine = create_engine(f"mysql+mysqldb://{username}:{password}@{host}/{database}")
metadata = MetaData()

print("Caricamento dati")
#Rilegge il database e carica nel dataframe
import ast
query = "SELECT *  FROM nlp "
df2 = pd.read_sql(query, con=engine)
df2['tokens'] = df2['tokens'].apply(ast.literal_eval) #Converte da stringa a lista (dal database legge come stringa)
#df2['vector'] = df2['vector'].apply(ast.literal_eval) #Converte da stringa a lista (dal database legge come stringa)



print("Addestramento...")
# Addestra il modello doc2Vec

#Addestramento Modello Doc2Vec e Generazione di una matrice di similarità
#Spunto:https://bytepawn.com/similar-posts-recommendation-with-doc2vec.html

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.test.utils import get_tmpfile

#Initialize & train a model:
idx_lookup = {df2['idprobl'][idx] : post for idx, post in enumerate(df2['tokens'])}
idx_lookup_desprobl = {df2['idprobl'][idx] : post for idx,  post in enumerate(df2['desprobl'])}
documents = [TaggedDocument(doc, [df2['idprobl'][i]]) for i, doc in enumerate(df2['tokens'])]
#(20 min per l'addestramento)
#model = Doc2Vec(documents, vector_size=100, alpha=0.025, min_count=1, workers=16, epochs=100)
#(10 min per l'addestramento)
#BEST 20 EPOCH 300 VECTORSIZE
#epochs = 30
#vectorsize = 100


# datetime object containing current date and time
now = datetime.now()
current_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
log = """
=====================================================
Addestramento modelli doc2Vec {current_datetime}
=====================================================
""".format(current_datetime=current_datetime)

for epochs in [1,10,30,50]:
    for vectorsize in [50,100,200]:
        start_time = time.time()
        print("Epochs:" + str(epochs))
        print("Vector size:" + str(vectorsize))
        label = '_epochs_'+str(epochs)+'_d'+str(vectorsize)
        
        fname = "models/my_doc2vec_model"+ label

        # Train model
        model = Doc2Vec(documents, vector_size=vectorsize, alpha=0.025, min_count=3, workers=20, epochs=epochs)

        #Persist model to disk
        model.save(fname)

        #Load model from disk
        
        #model = Doc2Vec.load(fname)  # you can continue


        print("Creazione dei vettori")
        # Crea i vettori di ciascun ticket usando il vettore addeestrato
        
        df2['vector'+label] = [model.infer_vector(tokens) for tokens in df2['tokens']]

        df2['vector'+label] = df2['vector'+label].apply(lambda x: str(x)) #prima di salvare la lista nel db converte l'array in stringa

        
        try:
            connection = engine.connect() 
              
            table_name = 'students'
              
            query = f'ALTER TABLE nlp ADD '+'vector'+label+' text ;'
            connection.execute(text(query)) 
        except Exception as e:
           # print(f"An error occurred: {str(e)}")
           print("colonna già esistente")

        
        exec_time = time.time() - start_time
        log += '''
Ephocs: {epochs}
Vector size: {vectorsize}
Execution time: {exec_time}ms
'''.format(epochs=epochs, vectorsize=vectorsize, exec_time=exec_time)
    
#e salva il dataframe nel database

df2['tokens'] = df2['tokens'].apply(lambda x: str(x)) #prima di salvare la lista nel db converte la lista in stringa))
# Avvia una transazione
with engine.connect() as connection:
    trans = connection.begin()
    try:
        
        # Elimina il contenuto della tabella
        #connection.execute(text("DELETE FROM nlp;"))

        # Inserisci il contenuto del DataFrame nella tabella
        #df.to_sql('nlp', con=connection, if_exists='append', index=False)
        df2.to_sql('nlp', con=connection, if_exists='replace', index=False)
        trans.commit()
    except Exception as e:
        # Se c'è un'eccezione, la transazione sarà rollbackata automaticamente
        trans.rollback()
        print(f"An error occurred: {str(e)}")
        
with open("training.log", "a") as myfile:
    myfile.write(log)        


'''

print("Fine")


#Rilegge il database e carica nel dataframe
import ast
query = "SELECT *  FROM nlp "
df3 = pd.read_sql(query, con=engine)
df3['tokens'] = df3['tokens'].apply(ast.literal_eval) #Converte da stringa a lista (dal database legge come stringa)
#df3['vector'] = df3['vector'].apply(ast.literal_eval) #Converte da stringa a numptndarray (dal database legge come stringa che inizia con il carattere [ e finisce con il carattere  ])

import numpy as np
#vector = np.fromstring(df3["vector"][0].replace("[", "").replace("]", ""), dtype=float, sep=' ')
vector = np.fromstring(df3["vector"][0].lstrip("[").rstrip("]"), dtype=float, sep=' ')

'''