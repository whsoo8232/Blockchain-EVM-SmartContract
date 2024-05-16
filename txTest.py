from web3 import Web3, HTTPProvider
from web3.exceptions import TimeExhausted
import os
import time
from Polygon_utils import *
from dotenv import load_dotenv

if __name__ == "__main__":
    ### common set ####
    load_dotenv('./Management/.env')

    network = "polygon"
    apikey = os.getenv("INFURA_API_KEY")

    account1 = os.getenv("MY_TESTMAIN")
    pk1 = os.getenv("MY_TESTMAIN_PK")
    account2 = os.getenv("MY_TESTTEST")
    pk2 = os.getenv("MY_TESTTEST_PK")

    tokenAddress = "0xc6608b41dC97f3c7B4A906974A4116AF96a4A119"
    tokenAbi = "Management/ERC20/MyPoL/source/MyPoL.abi"

    web3 = polygon_connect_web3(network, apikey)

    myContract = polygon_get_contract(web3, tokenAddress, tokenAbi)
    
    
    ### scripts ###
    coin = "ETH"
    currency = "USD"
    coinPrice = polygon_coin_spot_price(coin, currency)
    print(coinPrice)
    
    #startBlock = 0
    #endBlock = web3.eth.block_number
    #polygon_token_tx_list(web3, myContract, account1, startBlock, endBlock)
    
    #amt = 0.001
    #lst,tx_receipt = polygon_eth_transfer(web3, account1, pk1, account2, amt)
    #print(tx_receipt)
    #count = 100
    #while count:    
    #    tx_dict = polygon_ethereum_txList(web3)
    #    #print(tx_dict)
    #    print("----------------------------------------------")
    #    time.sleep(10)

    #eth_balanace = polygon_eth_getbalance(web3, account1)
    #print(eth_balanace)
    #amt = 0.01
    #gas, tx_receipt = polygon_eth_transfer(web3, account1, pk1, account2, amt)
    #print(f"{gas}, {tx_receipt}")
