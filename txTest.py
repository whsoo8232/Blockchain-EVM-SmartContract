import os
from dotenv import load_dotenv

from EVM_utils import *


if __name__ == "__main__":
    ### common set ####
    load_dotenv('.env')

    network = "amoy"
    apikey = os.getenv("INFURA_API_KEY")

    account1 = os.getenv("MY_TESTMAIN")
    pk1 = os.getenv("MY_TESTMAIN_PK")
    account2 = os.getenv("MY_TESTTEST")
    pk2 = os.getenv("MY_TESTTEST_PK")

    tokenAddress = "0xBafBe8Dc6b88868A7b58F6E5df89c3054dec93bB"
    tokenAbi = "./token.abi"

    web3 = polygon_connect_web3(network, apikey)

    contract = polygon_get_contract(web3, tokenAddress, tokenAbi)
    
    
    ### scripts ###
    addresses = ['0x2c18787A16E8Be7cF2cBCdC44AD97f616d1f7C0f','0x87460F55439594674891824dFF32ee5207d28A2f','0x8D17CA59aB97FAE4EDB200f11AA7E69f45d5Bae9','0x627e4495cB9CB339865157F38F2E9729ABaa5E12']
    amts = [1000, 1000, 1500, 1000]
    
    polygon_token_multi_send(web3, contract, account1, pk1, addresses, amts)
    