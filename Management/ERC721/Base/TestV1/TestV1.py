import os
from dotenv import load_dotenv

from web3 import Web3


def connect_web3(connect_host, apikey): #test done
    # Mainnet #
    if connect_host == 'ethereum':
        rpc_url = "https://mainnet.infura.io/v3/" + apikey
    elif connect_host == 'polygon':
        rpc_url = "https://polygon-mainnet.infura.io/v3/" + apikey
    # Testnet #
    elif connect_host == 'sepolia':
        rpc_url = "https://sepolia.infura.io/v3/" + apikey
    elif connect_host == 'amoy':
        rpc_url = "https://polygon-amoy.infura.io/v3/" + apikey
    elif connect_host == 'baseSepolia':
        rpc_url = "https://sepolia.base.org"
    else:
        return None
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    return web3


def get_contract(web3, contractAddress, contractAbi): #test done
    file = open(contractAbi, 'r', encoding='utf-8')
    contractaddress = web3.to_checksum_address(contractAddress)
    mycontract = web3.eth.contract(abi=file.read(), address=contractaddress)
    
    return mycontract


def NFT_isMinter(web3, mycontract, account):
    confirm_account = web3.to_checksum_address(account)
    role = mycontract.functions.isMinter(confirm_account).call()
    
    return role


def NFT_setMinter(web3, mycontract, From, From_pk, To, value=True):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    nonce = web3.eth.get_transaction_count(From_add)
    gas_price = web3.eth.gas_price
    tx = mycontract.functions.setMinter(To_add, value).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            'gasPrice': gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    print(tx_receipt)
    
    return tx_receipt


def NFT_mint(web3, mycontract, From, From_pk, ipfsUri, token_id): #test done
    From_add = web3.to_checksum_address(From)
    nonce = web3.eth.get_transaction_count(From_add)
    gas_price = web3.eth.gas_price
    tx = mycontract.functions.mint(From_add, token_id, ipfsUri).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            'gasPrice': gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    print(tx_receipt)
    
    return tx_receipt


if __name__ == "__main__":
    ### common set ####
    load_dotenv('../../../../.env')

    network = "baseSepolia"
    apikey = os.getenv("INFURA_API_KEY")

    account1 = os.getenv("MY_TESTMAIN")
    pk1 = os.getenv("MY_TESTMAIN_PK")
    account2 = os.getenv("MY_TESTTEST")
    pk2 = os.getenv("MY_TESTTEST_PK")

    web3 = connect_web3(network, apikey)
    
    NFT_contract_addr = "0x9eD9dBDd506ffD9c2d9A93d679109433E5a0d799"
    NFT_contract_abi = "./TestV1.abi"
    NFT_contract = get_contract(web3, NFT_contract_addr, NFT_contract_abi)
    
    ### scripts ###
    # NFT_setMinter(web3, NFT_contract, account1, pk1, account1, value=True)
    ipfsUri = "ipfs://QmYtyLu7qKjKo6LznfkzfDrWFjnfr4b9bog1e72vXQUDQk/braveKong.json"
    token_id = NFT_contract.functions.totalSupply().call() + 1
    NFT_mint(web3, NFT_contract, account1, pk1, ipfsUri, token_id)