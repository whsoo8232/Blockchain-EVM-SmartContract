#Common
import json
import os
import datetime
import requests
from web3 import Web3, HTTPProvider
from web3.exceptions import TimeExhausted
#ERC20
from eth_account.messages import encode_defunct, encode_structured_data, defunct_hash_message
import urllib
import time
import hashlib
import struct
# ERC721

### Common ###
def polygon_connect_web3(connect_host, apikey): #test done
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
    else:
        return None
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    return web3


def polygon_get_contract(web3, contractAddress, contractAbi): #test done
    file = open(contractAbi, 'r', encoding='utf-8')
    contractaddress = web3.to_checksum_address(contractAddress)
    mycontract = web3.eth.contract(abi=file.read(), address=contractaddress)
    
    return mycontract


def polygon_gasPrice(priceType=None):
    req = requests.get('https://api.polygonscan.com/api?module=gastracker&action=gasoracle&apikey=94GX5S8H6QIJVC2R9MX33V8AXMHC55DMXN')
    res = json.loads(req.content)
    if priceType == None:
        return res
    if priceType == "average":
        return res['result']['ProposeGasPrice']
    elif priceType == "safelow":
        return res['result']['SafeGasPrice']
    elif priceType == "fast":
        return res['result']['FastGasPrice']
    elif priceType == "low":
        return res['result']['suggestBaseFee']
    else:
        return res['result']['average']


def polygon_eth_getbalance(web3, account): #test done
    account = web3.to_checksum_address(account)
    balance = web3.from_wei(web3.eth.get_balance(account), 'ether')

    return balance


def polygon_eth_transfer(web3, From, From_pk, To, value): #test done
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    nonce = web3.eth.get_transaction_count(From_add)
    lst = []
    gas_estimate = web3.eth.estimate_gas({'from': From_add, 'to': To_add, 'value': web3.to_wei(value, "ether")})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
    tx = {
            'nonce': nonce,
            'from': From_add,
            'to': To_add,
            'value': web3.to_wei(value, 'ether'),
            'gas': gas_estimate,
            "gasPrice": gas_price
        }
    sign_tx = web3.eth.account.sign_transaction(tx,From_pk)
    tx_hash = web3.eth.send_raw_transaction(sign_tx.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)

    return lst, tx_receipt


#api docs from "https://docs.cloud.coinbase.com/sign-in-with-coinbase/docs/api-prices"##
#coin&currency require SYMBOL
def polygon_coin_spot_price(coin, currency):
    from coinbase.wallet.client import Client
    api_key = "organizations/1d87c8de-839b-4ef5-b73a-d6dca9bc9988/apiKeys/23fe4062-96b9-438c-b14f-e4b088fa8417"
    api_secret = "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEINMjhjFpmI1H+BJ4Vrq51mwomQtiZuaVLOV9jrsmYA++oAoGCCqGSM49\nAwEHoUQDQgAE/erXjwh+7HVnEdL4RjHb3Au6iCORFxA3SqvJDG6EpDxFDEtqtUtr\nWxl2NmPUaFK10tuPb6gvodjDZswH5aJKBw==\n-----END EC PRIVATE KEY-----\n"
    client = Client(api_key, api_secret)
    coinPair = coin + "-" + currency
    priceData = client.get_spot_price(currency_pair = coinPair)
    return priceData #return Dict


#ethereum block generation delay : 12sec
def polygon_tx_list(web3,address):
    import pickle
    tx_dictionary = {}
    endBlock = web3.eth.block_number
    startBlock = endBlock - 1
    print(f"Started filtering through block number {startBlock} to {endBlock} for transactions")
    for x in range(startBlock, endBlock):
        block = web3.eth.get_block(x, True)
        for transaction in block.transactions:
            if transaction['to'] == address or transaction['from'] == address:
                with open("transactions.pkl", "wb") as f:
                    hashStr = transaction['hash'].hex()
                    tx_dictionary[hashStr] = transaction
                    pickle.dump(tx_dictionary, f)
                f.close()
    print(f"Finished searching blocks {startBlock} through {endBlock} and found {len(tx_dictionary)} transactions")
    
    return tx_dictionary


def polygon_tx_list2(web3):
    import pickle
    tx_dictionary = {}
    endBlock = web3.eth.block_number
    startBlock = endBlock - 1
    print(f"Started filtering through block number {startBlock} to {endBlock} for transactions")
    for x in range(startBlock, endBlock):
        block = web3.eth.get_block(x, True)
        for transaction in block.transactions:
            print(transaction)
            with open("transactions.pkl", "wb") as f:
                hashStr = transaction['hash'].hex()
                tx_dictionary[hashStr] = transaction
                pickle.dump(tx_dictionary, f)
            f.close()
    print(f"Finished searching blocks {startBlock} through {endBlock} and found {len(tx_dictionary)} transactions")
    
    #return tx_dictionary


def polygon_wait_for_tx_receipt(web3, txHash):
    gnc_dict = {}
    retCnt = 0
    while True:
        try:
            tx_receipt = web3.eth.wait_for_transaction_receipt(txHash, timeout=0.001)
            gnc_dict  = {'error': False, 'transactionHash': web3.to_hex(tx_receipt.transactionHash), 'blockNumber': tx_receipt.blockNumber,
                        'blockhash': web3.to_hex(tx_receipt.blockHash), 'logsBloom': web3.to_hex(tx_receipt.logsBloom),
                        'tx_fee': (tx_receipt.effectiveGasPrice * tx_receipt.gasUsed) * web3.from_wei(1, "ether"), 'to': tx_receipt.to}
            break
        except TimeExhausted as e:
            retCnt += 1
            if retCnt > 3:
                gnc_dict = {'error': True, 'transactionHash': txHash}
                break

    return gnc_dict


### ERC721 ###
def polygon_NFT_contractName(mycontract):
     name = mycontract.functions.name().call()
     
     return name


def polygon_NFT_contractSymbol(mycontract):
     symbol = mycontract.functions.name().call()
     
     return symbol


def polygon_NFT_totalSuply(mycontract):
    total_token = mycontract.functions.totalSupply().call()

    return total_token


def polygon_NFT_owner(mycontract, token_id):
    token_owner = mycontract.functions.ownerOf(token_id).call()

    return token_owner


def polygon_NFT_isOwner(web3, mycontract, account):
    confirm_account = web3.to_checksum_address(account)
    role = mycontract.functions.owner().call()
    owner_address = web3.to_checksum_address(role)
    if confirm_account == owner_address:
        value = True
    else :
        value = False

    return value


def polygon_NFT_change_ownership(web3, mycontract, From, From_pk, To):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    nonce = web3.eth.get_transaction_count(From_add)
    lst = []
    gas_estimate = mycontract.functions.transferOwnership(To_add).estimate_gas({'from': From_add})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
    tx = mycontract.functions.transferOwnership(To_add).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            'gasPrice': gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_NFT_isMinter(web3, mycontract, account):
    confirm_account = web3.to_checksum_address(account)
    role = mycontract.functions.isMinter(confirm_account).call()
    
    return role


def polygon_NFT_setMinter(web3, mycontract, From, From_pk, To, value=True):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    nonce = web3.eth.get_transaction_count(From_add)
    lst = []
    gas_estimate = mycontract.functions.setMinter(To_add, value).estimate_gas({'from': From_add})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
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
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_NFT_isPauser(web3, mycontract, account):
    confirm_account = web3.to_checksum_address(account)
    role = mycontract.functions.isPauser(confirm_account).call()
    
    return role


def polygon_NFT_setPauser(web3, mycontract, From, From_pk, To, value=True):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    nonce = web3.eth.get_transaction_count(From_add)
    lst = []
    gas_estimate = mycontract.functions.setPauser(To_add, value).estimate_gas({'from': From_add})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
    tx = mycontract.functions.setPauser(To_add, value).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            'gasPrice': gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_NFT_mint(web3, mycontract, From, From_pk, ipfsUri, token_id): #test done
    From_add = web3.to_checksum_address(From)
    nonce = web3.eth.get_transaction_count(From_add)
    lst = []
    gas_estimate = mycontract.functions.mint(From_add, token_id, ipfsUri).estimate_gas({'from': From_add})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
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
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_NFT_airdrop_mint(web3, mycontract, From, From_pk, To, ipfsUri):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    token_id = polygon_NFT_totalSuply(web3, mycontract) + 1
    nonce = web3.eth.get_transaction_count(From_add)
    lst = []
    gas_estimate = mycontract.functions.mint(To_add, token_id, ipfsUri).estimate_gas({'from': From_add})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
    tx = mycontract.functions.mint(To_add, token_id, ipfsUri).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            'gasPrice': gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_burn(web3, mycontract, From, From_pk, token_id):
    From_add = web3.to_checksum_address(From)
    nonce = web3.eth.get_transaction_count(From_add)
    lst=[]
    gas_estimate = mycontract.functions.burn(token_id).estimate_gas({'from': From_add})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
    tx =  mycontract.functions.burn(token_id).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            'gasPrice': gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_NFT_transferFrom(web3, mycontract, From, From_pk, To, token_id):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    nonce = web3.eth.get_transaction_count(From_add)
    lst=[]
    gas_estimate = mycontract.functions.transferFrom(From_add, To_add, token_id).estimate_gas({'from': From_add})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
    tx =  mycontract.functions.transferFrom(From_add, To_add, token_id).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            'gasPrice': gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_NFT_list(web3, mycontract, startBlock, lastblock, token_id=None):
    tx_list = []
    if token_id is None:
        myFilter = mycontract.events.Transfer.createFilter(fromBlock=startBlock)
    else :
        myFilter = mycontract.events.Transfer.createFilter(fromBlock=startBlock, argument_filters={ 'tokenId': token_id})
    txs = myFilter.get_all_entries()
    for tx in txs:
        tx_hash = (tx.transactionHash).hex()
        getblock = web3.eth.get_block(tx.blockNumber).timestamp
        date = datetime.datetime.fromtimestamp(int(getblock)).strftime('%Y-%m-%d %H:%M:%S')
        tx_data = {'from': tx.args['from'], 'to': tx.args['to'], 'tokenId': tx.args['tokenId'], 'event': tx.event,'transactionHash': tx_hash, 'blockNumber': tx.blockNumber, 'date': date }
        tx_list.append(tx_data)

    return tx_list


### ERC20 ###
def polygon_token_contractName(mycontract): #test done
     name = mycontract.functions.name().call()
     
     return name
 
 
def polygon_token_contractSymbol(mycontract): #test done
     symbol = mycontract.functions.name().call()
     
     return symbol


def polygon_metic_get_balance(web3, account): #test done
    account = web3.to_checksum_address(account)
    balance = web3.from_wei(web3.eth.get_balance(account), 'ether')
	
    return balance


def polygon_token_get_balance(mycontract, account): #test done
    token_balance = mycontract.functions.balanceOf(account).call()
    
    return token_balance


def polygon_token_totalSuply(mycontract): #test done
    total_token = mycontract.functions.totalSupply().call()
    
    return total_token


def polygon_token_approve(web3, mycontract, From, From_pk, To, value):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    nonce = web3.eth.get_transaction_count(From_add)
    gas_estimate = mycontract.functions.approve(To_add,value).estimate_gas({'from': From_add})
    lst = []
    gas_price = web3.eth.gas_price
    before_tx_fee = web3.from_wei(gas_estimate * gas_price, 'Ether')
    lst.append(before_tx_fee)
    tx = mycontract.functions.approve(To_add,value).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            "gasPrice": gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    if before_tx_fee == after_tx_fee:
        lst.append('true')
    else:
        lst.append('false')
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_token_mint(web3, mycontract, owner, owner_pk, value): #test done
    owner_add = web3.to_checksum_address(owner)
    nonce = web3.eth.get_transaction_count(owner_add)
    amount = value * 10**mycontract.functions.decimals().call()
    gas_estimate = mycontract.functions.mint(owner_add,amount).estimate_gas({'from': owner_add})
    lst = []
    gas_price = web3.eth.gas_price
    before_tx_fee = web3.from_wei(gas_estimate * gas_price, 'Ether')
    lst.append(before_tx_fee)
    tx = mycontract.functions.mint(owner_add,amount).build_transaction(
        {
            'from': owner_add,
            'nonce': nonce,
            "gasPrice": gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, owner_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    if before_tx_fee == after_tx_fee:
        lst.append('true')
    else:
        lst.append('false')
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_token_airdrop_mint(web3, mycontract, From, From_pk, To, value):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    nonce = web3.eth.get_transaction_count(From_add)
    amount = value * 10**mycontract.functions.decimals().call()
    gas_estimate = mycontract.functions.mint(To_add,amount).estimate_gas({'from': From_add})
    lst = []
    print(gas_estimate)
    gas_price = web3.eth.gas_price
    print(gas_price)
    before_tx_fee = web3.from_wei(gas_estimate * gas_price, 'Ether')
    lst.append(before_tx_fee)
    print(before_tx_fee)
    tx = mycontract.functions.mint(To_add,amount).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            "gasPrice": gas_price
        }
    )
    print(tx)
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    if before_tx_fee == after_tx_fee:
        lst.append('true')
    else:
        lst.append('false')
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_token_burn(web3, mycontract, owner, owner_pk, value):
    owner_add = web3.to_checksum_address(owner)
    nonce = web3.eth.get_transaction_count(owner_add)
    amount = value * 10**mycontract.functions.decimals().call()
    gas_estimate = mycontract.functions.burn(amount).estimate_gas({'from': owner_add})
    lst = []
    print(gas_estimate)
    gas_price = web3.eth.gas_price
    print(gas_price)
    before_tx_fee = web3.from_wei(gas_estimate * gas_price, 'Ether')
    lst.append(before_tx_fee)
    print(before_tx_fee)
    tx = mycontract.functions.burn(amount).build_transaction(
        {
            'from': owner_add,
            'nonce': nonce,
            "gasPrice": gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, owner_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    if before_tx_fee == after_tx_fee:
        lst.append('true')
    else:
        lst.append('false')
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_token_transferFrom(web3, mycontract, From, From_pk, To, value):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    amount = value * 10**mycontract.functions.decimals().call()
    nonce = web3.eth.get_transaction_count(From_add)
    gas_estimate = mycontract.functions.transfer(To_add,amount).estimate_gas({'from': From_add})
    lst = []
    gas_price = web3.eth.gas_price
    before_tx_fee = web3.from_wei(gas_estimate * gas_price, 'Ether')
    lst.append(before_tx_fee)
    tx = mycontract.functions.transfer(To_add,amount).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            "gasPrice": gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    if before_tx_fee == after_tx_fee:
        lst.append('true')
    else:
        lst.append('false')
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_token_multi_send(web3, mycontract, From, From_pk, To_list, amt_list):
    for i in range(len(amt_list)):
        amt_list[i] =  amt_list[i] * 10**mycontract.functions.decimals().call()
    
    From_add = web3.to_checksum_address(From)
    nonce = web3.eth.get_transaction_count(From_add)
    gas_price = web3.eth.gas_price
    tx = mycontract.functions.multisend(To_list,amt_list).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            "gasPrice": gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    print(tx_receipt)


def polygon_verify_allowance(web3, mycontract, From, To):
     verify = mycontract.functions.allowance(From,To).call()
     
     print(verify)


def to_32byte_hex(val):
  return Web3.to_hex(Web3.to_bytes(val).rjust(32, b'\0'))


def polygon_permit_hash(web3, mycontract, token_add, From, From_pk, To, deadline, amount):
    From_add = web3.to_checksum_address(From)
    To_add =  web3.to_checksum_address(To)
    nonce = mycontract.functions.nonces(From_add).call()
    contract_name = mycontract.functions.name().call()
    msg ={
    "domain": {
        "name": contract_name,
        "version": "1",
        "chainId": int(web3.net.version),
        "verifyingContract": token_add
    },
    "message": {
        "owner": From_add,
        "spender": To_add,
        "value": amount,
        "nonce": int(nonce),
        "deadline": deadline
    },
    "primaryType": "Permit",
    "types": {
        "EIP712Domain": [
        {
            "name": "name",
            "type": "string"
        },
        {
            "name": "version",
            "type": "string"
        },
        {
            "name": "chainId",
            "type": "uint256"
        },
        {
            "name": "verifyingContract",
            "type": "address"
        }
        ],
        "Permit": [
        {
            "name": "owner",
            "type": "address"
        },
        {
            "name": "spender",
            "type": "address"
        },
        {
            "name": "value",
            "type": "uint256"
        },
        {
            "name": "nonce",
            "type": "uint256"
        },
        {
            "name": "deadline",
            "type": "uint256"
        }
        ]
    }
    }
    new_msg = json.loads(json.dumps(msg))
    new_msg['domain']['version'] = str(new_msg['domain']['version'])
    encoded_data=encode_structured_data(new_msg)
    print(encoded_data)
    owner_pk = web3.eth.account.from_key(From_pk)
    signature = owner_pk.sign_message(encoded_data)
    print(signature)
    v = int(signature.v)
    r = to_32byte_hex(signature.r)
    s = to_32byte_hex(signature.s)
    confirm = web3.eth.account.recover_message(encoded_data ,signature = signature.signature)
    print(confirm)
    
    return v,r,s


def polygon_token_change_ownership(web3, mycontract, From, From_pk, To):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    nonce = web3.eth.get_transaction_count(From_add)
    lst = []
    gas_estimate = mycontract.functions.transferOwnership(To_add).estimate_gas({'from': From_add})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
    tx = mycontract.functions.transferOwnership(To_add).build_transaction(
        {
            'from': From_add,
            'nonce': nonce,
            'gasPrice': gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, From_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    print(tx_receipt)
    
    return lst, tx_receipt


def polygon_token_tx_list(mycontract, address, startBlock, endBlock):
    etherscanApi = "https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress=" + str(mycontract.address) + "&address=" + str(address) + "&startblock=" + str(startBlock) + "&endblock=" + str(endBlock) + "&page=1&offset=5&sort=asc&apikey=BRB7ZWGGJWUGGY6YRP68RAU4NGPTVH1GB2"
    req = requests.get(etherscanApi)
    tx_list = req.json()
    
    return tx_list
