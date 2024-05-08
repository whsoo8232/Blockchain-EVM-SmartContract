from web3 import Web3, HTTPProvider
from web3.exceptions import TimeExhausted
import json
import requests
import os
import datetime

def polygon_connect_web3(network, apikey):
    if network is None:
        url = "http://localhost:8545"
    elif network == "amoy":
        url = "https://rpc-amoy.polygon.technology"
    elif network == "polygon":
        url = "https://polygon-mainnet.infura.io/v3/" + apikey
    else:
        url = "http://localhost:8545"
    web3 = Web3(Web3.HTTPProvider(url))
    
    return web3


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


def polygon_eth_getbalance(web3, account):
    account = web3.to_checksum_address(account)
    balance = web3.from_wei(web3.eth.get_balance(account), 'ether')

    return balance


def polygon_metic_transfer(web3, From, From_pk, To, value):
    From_add = web3.toChecksumAddress(From)
    To_add = web3.toChecksumAddress(To)
    nonce = web3.eth.get_transaction_count(From_add)
    lst = []
    gas_estimate = web3.eth.estimateGas({'from': From_add, 'to': To_add, 'value': web3.toWei(value, "ether")})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
    tx = {
            'nonce': nonce,
            'to': To_add,
            'value': web3.toWei(value, 'ether'),
            'gas': gas_estimate,
            "gasPrice": web3.toWei(gas_price , 'gwei'),
        }
    sign_tx = web3.eth.account.signTransaction(tx,From_pk)
    tx_hash = web3.eth.sendRawTransaction(sign_tx.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)

    return lst, tx_receipt


def polygon_get_contract(web3, contractAddress, contractAbi):
    file = open(contractAbi, 'r', encoding='utf-8')
    contractaddress = web3.to_checksum_address(contractAddress)
    mycontract = web3.eth.contract(abi=file.read(), address=contractaddress)
    
    return mycontract


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


def polygon_NFT_uri(mycontract, token_id):
    tokenid_uri = mycontract.functions.tokenURI(token_id).call()

    return tokenid_uri


def polygon_wait_for_transaction_receipt(web3, txHash):
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

    return lst, tx_receipt


def polygon_NFT_get_imageUrl(tokenuri):
    with url.request.urlopen(tokenuri) as url:
        s = url.read()
        sdata = json.loads(s)
        imageurl = sdata['image']
        name = sdata['name']

        return imageurl, name


def polygon_NFT_snapshot(web3, mycontract):
    from web3.middleware import geth_poa_middleware # type: ignore
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    total = polygon_NFT_totalSuply(web3, mycontract)
    owner_list = []
    for i in range(1, total + 1):
        try:
            owner = polygon_NFT_owner(web3, mycontract, i)
            uri = polygon_NFT_uri(web3, mycontract, i)
            owner_data = {'TokenId': i, 'Owner': owner, 'URI': uri}
            owner_list.append(owner_data)
        except Exception as e:
            continue

    return owner_list


def polygon_NFT_owner_mint(web3, mycontract, From, From_pk, jsonUri, token_id):
    From_add = web3.to_checksum_address(From)
    nonce = web3.eth.get_transaction_count(From_add)
    lst = []
    gas_estimate = mycontract.functions.mint(From_add, token_id, jsonUri).estimate_gas({'from': From_add})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
    tx = mycontract.functions.mint(From_add, token_id, jsonUri).build_transaction(
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

    return lst, tx_receipt


def polygon_NFT_airdrop_mint(web3, mycontract, From, From_pk, To, jsonUri):
    From_add = web3.to_checksum_address(From)
    To_add = web3.to_checksum_address(To)
    token_id = polygon_NFT_totalSuply(web3, mycontract) + 1
    nonce = web3.eth.get_transaction_count(From_add)
    lst = []
    gas_estimate = mycontract.functions.mint(To_add, token_id, jsonUri).estimate_gas({'from': From_add})
    lst.append(gas_estimate)
    gas_price = web3.eth.gas_price
    lst.append(gas_price)
    tx = mycontract.functions.mint(To_add, token_id, jsonUri).build_transaction(
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

    return lst, tx_receipt

#nonce err
#def polygon_NFT_multimint(web3, mycontract, sender_add, sender_pk, receiver_add, ipfsUris):
    nonce = web3.eth.get_transaction_count(sender_add)
    senderAddress = web3.to_checksum_address(sender_add)
    receiver_add = web3.to_checksum_address(receiver_add)
    receiver_adds = []
    token_ids = []
    for i in range(0, len(ipfsUris)):
        receiver_adds.append(receiver_add)
        token_ids.append(polygon_NFT_totalsuply(web3, mycontract) + i + 1)
    gas_estimate = mycontract.functions.multimint(receiver_adds, token_ids, ipfsUris).estimate_gas({'from': senderAddress})
    gas_price = web3.eth.gas_price
    tx = mycontract.functions.multimint(receiver_adds, token_ids, ipfsUris).build_transaction(
        {
            'from': senderAddress,
            'nonce': nonce,
            'gasPrice': gas_price
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, sender_pk)
    txHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(txHash)
    after_tx_fee = web3.from_wei(tx_receipt.effectiveGasPrice * tx_receipt.gasUsed, 'Ether')
    lst.append(after_tx_fee)
    
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


def polygon_NFT_list2(web3, mycontract):
    my_filter = mycontract.events.Transfer.createFilter(fromBlock='latest')

    while True:
        for event in my_filter.get_new_entries():
            print(event)

