
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from uuid import uuid4
from bson.objectid import ObjectId
import datetime

from blockchain import Blockchain
from admin import Admin
from voter import Voter

# Creating a Web App
app = Flask(__name__)
app.secret_key = "vote4u"
# Creating an address for the node on Port 5000
# node_address = str(uuid4()).replace('-', '')

#app
@app.before_first_request
def initialization():
    if len(Blockchain.chain) == 0:
        Blockchain.create_block(nonce=0, previous_hash='0000', data=[])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help():
    return render_template('help.html')

#admin
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/authenticate', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']

    admin = Admin.getAdmin({'username':username,'password':password})

    if admin is None:
        session.pop('admin', None)
        return redirect(url_for('admin'))
    else:
        session['admin'] = username
        return redirect(url_for('dashboard'))

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))
""" 
@app.route('/admin/adduser')
def adduser():
    if 'username' in session:
        return render_template('adduser.html')
    else:
        return redirect(url_for('admin'))
"""
@app.route('/admin/dashboard')
def dashboard():
    if 'admin' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('admin'))

@app.route('/admin/setElection', methods=['GET', 'POST'])
def setElection():
    if request.method == 'GET':
        if 'admin' in session:
            return render_template('setElection.html')
        else:
            return redirect(url_for('admin'))
    elif request.method == 'POST':
        description = request.form['description']
        # edate = datetime.datetime.strptime(request.form['electionDate'],'%Y-%m-%d')
        print(description)
        return redirect(url_for('dashboard'))

@app.route('/admin/approveVoter')
def approveVoter():
    if 'admin' in session:
        voters = Voter.getVoters({'status':False})
        return render_template('approveVoter.html', Voters=voters)
    else:
        return redirect(url_for('admin'))

@app.route('/admin/approveCandidate')
def approveCandidate():
    if 'admin' in session:
        voters = Voter.getVoters({'status':False})
        return render_template('approveCandidate.html', Candidates=voters)
    else:
        return redirect(url_for('admin'))

@app.route('/admin/view/<id>/')
def view(id):
    if 'admin' in session:
        voter = Voter.getVoter({'_id': ObjectId(id)})
        return render_template('viewVoter.html', Voter = voter)
    else:
        return redirect(url_for('admin'))

@app.route('/admin/approve/<id>/')
def approvedVoter(id):
    if 'admin' in session:
        Voter.updateVoter({'_id':ObjectId(id)}, {'$set':{'status':True}})
        return redirect(url_for('approveVoter'))
    else:
        return redirect(url_for('admin'))

#voter
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registerCandidate')
def registerCandidate():
    if 'voter' in session:
        return render_template('registerCandidate.html')
    else:
        return redirect(url_for('login'))

@app.route('/voter/authenticate', methods=['POST'])
def voter_authenticate():
    username = request.form['username']
    password = request.form['password']

    voter = Voter.getVoter({'username':username,'password':password})

    if voter is None:
        session.pop('voter', None)
        return redirect(url_for('login'))
    else:
        session['voter'] = username
        return redirect(url_for('home'))

@app.route('/voter/register', methods=['POST'])
def voter_register():
    username = request.form['username']
    password = request.form['password']

    voter = Voter.getVoter({'username':username})

    if voter is None:
        voter = Voter(username = username, password = password)
        voter.addVoter()
        session['voter'] = username
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/voter/logout')
def voter_logout():
    session.pop('voter', None)
    return redirect(url_for('login'))

@app.route('/voter/home')
def home():
    if 'voter' in session:
        username = session['voter']
        voter = Voter.getVoter({'username':username})
        return render_template('home.html', Voter = voter)
    else:
        return redirect(url_for('login'))

@app.route('/voter/profile')
def profile():
    if 'voter' in session:
        username = session['voter']
        voter = Voter.getVoter({'username':username})
        return render_template('profile.html',Voter = voter)
    else:
        return redirect(url_for('login'))

@app.route('/voter/update', methods=['POST'])
def voter_update():
    name = request.form['name']
    DOB = request.form['DOB']
    address = request.form['address']
    state = request.form['state']
    constituency = request.form['constituency']
    mobile = request.form['mobile']
    email = request.form['email']
    aadhaar = request.form['aadhaar']
    status = False

    new = {
        'name' : name,
        'DOB' : DOB,
        'address' : address,
        'state' : state,
        'constituency' : constituency,
        'mobile' : mobile,
        'email' : email,
        'aadhaar' : aadhaar,
        'status' : status
    }
    Voter.updateVoter({'username':session['voter']}, {'$set': new})
    return redirect(url_for('profile'))

@app.route('/vote')
def vote():
    return render_template('vote.html')

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    data = {
        'voter':request.form['voter'],
        'voteFor':request.form['voteFor'],
        'constituency':request.form['constituency']
    }
    Blockchain.add_data(data = data)
    response = {'message': 'This transactional-data will be added to Blockchain'}
    return jsonify(response), 201

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {
        'chain': Blockchain.chain,
        'length': len(Blockchain.chain)
    }
    return jsonify(response), 200

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prev_block = Blockchain.chain[-1]
    prev_hash = Blockchain.hash_block(prev_block)
    block = Blockchain.create_block(nonce=0, previous_hash=prev_hash, data=Blockchain.data)
    response = {
        'message': 'Congratulations, you just mined a block!',
        'block': block
    }
    Blockchain.data = []
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = Blockchain.is_chain_valid(Blockchain.chain)
    if is_valid:
        response = {
            'message': 'All good. The Blockchain is valid.'
        }
    else:
        response = {
            'message': 'Problem. The Blockchain is not valid.'
        }
    return jsonify(response), 200

'''
# Decentralizing our Blockchain
'''
# Connecting new nodes
@app.route('/connect_node', methods = ['GET'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        Blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Hadcoin Blockchain now contains the following nodes:',
                'total_nodes': list(Blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = Blockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message': 'The nodes had different chains so the chain was replaced by the longest one.',
            'new_chain': Blockchain.chain
        }
    else:
        response = {
            'message': 'All good. The chain is the largest one.',
            'actual_chain': Blockchain.chain
        }
    return jsonify(response), 200

# Running the app
if __name__ == '__main__':
	app.run(host='0.0.0.0',port='8000')