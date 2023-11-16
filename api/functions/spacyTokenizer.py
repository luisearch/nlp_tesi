#Preprocessamento del Testo con Spacy
#!pip install spacy
#!python -m spacy download it_core_news_lg
import spacy

import it_core_news_lg
nlp = it_core_news_lg.load()

def preprocessTextSpacy(input):
    blacklist_words = ['ciao', 'cortesemente', 'buongiorno', 'grazie', 'cordiali', 'saluti', 'i', '\r\n\r\n', '\r\n']
    tokens = nlp(str(input).lower())
    output = []
    for token in tokens:
        if not token.is_stop and not token.is_punct :
            if str(token) not in list(blacklist_words):
                output.append( token.lemma_)
    return output