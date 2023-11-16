# index.py

from flask import Flask, jsonify, request

app = Flask(__name__)

incomes = [
    { 'description': 'salary', 'amount': 5000 }
]


import functions.topNTickets as tnt
import functions.topNTicketsQuery as tntq
import functions.codifyNewTicket as cnt

@app.route('/top-n-tickets')  
def topNSimilarTikets():
    aaprobl = request.args.get('aaprobl')
    print(aaprobl)
    nroprobl = request.args.get('nroprobl')
    print(nroprobl) 
    n = int(request.args.get('n'))
    print(n) 
    print(type(n) )
    return tnt.getTopNSimilarTickets(aaprobl, nroprobl, n)
   
@app.route('/top-n-tickets-by-query')  
def topNSimilarTicketsByQuery():
    text = request.args.get('text')
    n = int(request.args.get('n'))
    return tntq.getTopNSimilarTicketsByQuery(text, n)  
    
@app.route('/codify-new-ticket')  
def codifyNewTicket():
    aaprobl = request.args.get('aaprobl')
    nroprobl = request.args.get('nroprobl')
    desprobl = request.args.get('desprobl')
    return cnt.codifyNewTicket(aaprobl, nroprobl, desprobl)    
   
################
   
@app.route('/incomes')
def get_incomes():
    return jsonify(incomes)


@app.route('/incomes', methods=['POST'])
def add_income():
    incomes.append(request.get_json())
    return '', 204
    
    