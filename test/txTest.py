import os
from dotenv import load_dotenv

from EVM_utils import *


if __name__ == "__main__":
    ### common set ####
    load_dotenv('../.env')
    INFURA_API_KEY = os.getenv("INFURA_API_KEY")
    QUICKNODE_BASE_SEPOLIA_ENDPOINT_KEY = os.getenv("QUICKNODE_BASE_SEPOLIA_ENDPOINT_KEY")
    MY_TESTMAIN = os.getenv("MY_TESTMAIN")
    MY_TESTMAIN_PK = os.getenv("MY_TESTMAIN_PK")
    MY_TESTTEST = os.getenv("MY_TESTTEST")
    MY_TESTTEST_PK = os.getenv("MY_TESTTEST_PK")
    
    network = "base_sepolia"
    base_sepolia_web3 = connect_web3(network, QUICKNODE_BASE_SEPOLIA_ENDPOINT_KEY)

    contract_addr = "0x109b9Ed66AcEF53BEE27d274CcAD518A5b8ef338"
    contract_abi = "./baseARTC.abi"
    contract = get_contract(base_sepolia_web3, contract_addr, contract_abi)


    ### scripts ###
    bal = contract.functions.balanceOf(MY_TESTMAIN).call()
    print(bal)
