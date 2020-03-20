
import hashlib, json
import datetime
import requests
from ipfs import IPFS
from urllib.parse import urlparse

class Blockchain:

    chain = []
    data = []
    nodes = set()

    @staticmethod
    def create_block(nonce=0, previous_hash = '0000', data = []):
        while True:
            block = {
                'index' : len(Blockchain.chain)+1,
                'timestamp' : datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S'),
                'nonce' : nonce,
                'previous_hash' : previous_hash,
                'data' : data
            }
            
            block = json.dumps(block, separators=(',',':'))
            block = json.loads(block)
            
            if str(Blockchain.hash_block(block))[:4] == '0000':
                break
            else :
                nonce+=1
        Blockchain.chain.append(block)
        return block

    @staticmethod
    def add_data(data = {}):
        Blockchain.data.append(data)

    @staticmethod
    def hash_block(block):
        block = json.dumps(block, separators=(',',':')).encode()
        return hashlib.sha256(block).hexdigest()

    @staticmethod
    def is_chain_valid(chain):
        prev_hash = '0000'
        for block in chain:
            print(block)
            if str(Blockchain.hash_block(block))[:4] != '0000' or block['previous_hash'] != prev_hash:
                return False
            prev_hash = Blockchain.hash_block(block)
        return True

    #decentralization
    @staticmethod
    def add_node(address):
        parsed_url = urlparse(address)
        Blockchain.nodes.add(parsed_url.netloc)

    @staticmethod
    def replace_chain():
        network = Blockchain.nodes
        longest_chain = None
        max_length = len(Blockchain.chain)
        for node in network:
            response = requests.get(f'https://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and Blockchain.is_chain_valid(Blockchain.chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            Blockchain.chain = longest_chain
            return True
        return False
