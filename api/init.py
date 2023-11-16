#Inizializzazione ambiente


#!pip install sqlalchemy
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, text
from sqlalchemy.types import *

# Crea una connessione utilizzando SQLAlchemy 
username = 'root'
password = ''
host = 'localhost'
database = 'itaca'

print("step1")
try:
    engine = create_engine(f"mysql+mysqldb://{username}:{password}@{host}/{database}")
    metadata = MetaData()
    
    # Definisci e crea la tabella 'nlp'
    nlp = Table('nlp', metadata,
                 # Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('aaprobl', Integer()),
                  Column('nroprobl', Integer()),
                  Column('desprobl', Text()),
                  Column('idprobl', String(10)),
                  Column('tokens', Text()),
                 # Column('vector', String(400))
                  )
    nlp.create(engine)
    print("Tabella itaca.nlp creata")    

    
except Exception as e:
    msg = "tabella nlp già esistente";
   # print(str(e)) #problema in fase di creazione nuovi campi della tabella itaca.itpbc

print('step2')   

'''
Recupero dal database tutti i ticket della tabella itpbc e li metto in un dataframe
'''    
# Esegui la query SELECT e inserisci il risultato in un DataFrame
query = "SELECT aaprobl, nroprobl, desprobl  FROM itpbc"# LIMIT 1000"
df = pd.read_sql(query, con=engine)

'''
Dal dataframe ottenuto genero i tokens e salvo il dataframe nella tabella nlp
'''
import functions.spacyTokenizer as st
df['tokens'] = [st.preprocessTextSpacy(des) for des in df['desprobl'] ]
#df['vector'] = ['' for des in df['desprobl'] ]
df['idprobl'] = df['aaprobl'].map(str) + df['nroprobl'].map(str)

print("step3")


# Salva il DataFrame nella tabella 'nlp'

df['tokens'] = df['tokens'].apply(lambda x: str(x)) #prima di salvare la lista nel db converte la lista in stringa))
#df['vector'] = df['vector'].apply(lambda x: str(x)) #prima di salvare la lista nel db converte l'array in stringa))

# Avvia una transazione
with engine.connect() as connection:
    trans = connection.begin()
    try:
        # Elimina il contenuto della tabella
        #connection.execute(text("DELETE FROM nlp;"))

        # Inserisci il contenuto del DataFrame nella tabella
        #df.to_sql('nlp', con=connection, if_exists='append', index=False)
        #Guida to_sql best practice: https://medium.com/@erkansirin/worst-way-to-write-pandas-dataframe-to-database-445ec62025e0
        
        df_schema = {
          "id": Integer,   
          "aaprobl": Integer,   
          "nroprobl": Integer,  
          "idprobl":String(10),
          "desprobl": Text,
          "tokens": Text,
        }
        df.to_sql('nlp', con=connection, if_exists='replace', index=False,dtype=df_schema)
        trans.commit()
    except Exception as e:
        # Se c'è un'eccezione, la transazione sarà rollbackata automaticamente
        trans.rollback()
        print(f"An error occurred: {str(e)}")

