from web3 import Web3, HTTPProvider
from web3.exceptions import TimeExhausted
import json
import requests
import sys, os
sys.path.insert(1, '../../../')
from Polygon_utils import *
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv('/home/whsoo8232/my-EVM-smartContract/Management/.env')

    network = "amoy"
    apikey = os.getenv("INFURA_API_KEY")

    account1 = os.getenv("MY_TESTMAIN")
    pk1 = os.getenv("MY_TESTMAIN_PK")
    account2 = os.getenv("MY_TESTTEST")
    pk2 = os.getenv("MY_TESTTEST_PK")


    tokenAddress = "0x296fA9e97805d42D312D1A0085A6Ca14EC816B79"
    tokenAbi = "./source/TestCoin.abi"

    web3 = polygon_connect_web3(network, apikey)

    myContract = polygon_get_contract(web3, tokenAddress, tokenAbi)
    
    amt = 10000000
    polygon_token_mint(web3, myContract, account1, pk1, amt)
