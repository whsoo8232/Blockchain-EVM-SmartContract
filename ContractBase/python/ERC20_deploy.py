# os
import sys
import os
import subprocess

# logging
import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler

# file
from deployContract import *

#env
from dotenv import load_dotenv
load_dotenv('../../.env')

if __name__ == "__main__":
    python_pgm = os.path.basename(sys.argv[0])

    logger = polygon_set_logger(python_pgm)
    logger.setLevel(logging.DEBUG)
    
    network = "baseSepolia"

    rpcUrlKey = os.getenv("QUICKNODE_BASE_SEPOLIA_ENDPOINT_KEY")
    etherscanKey = ""

    ownerPK = "0x119b1e18189153f894f5ccee62a23dac9233df290e159ed6b2d727bad19a142b"


    tokenType = "ERC20"
    targetTokenName = "ARTC"
    targetSymbolName = "ARTC"
    targetAmount = 10000000000

    retCode, retMessage = polygon_deploy_contract(network, rpcUrlKey, etherscanKey, ownerPK, tokenType, targetTokenName, targetSymbolName, targetAmount, logger, python_pgm)
    print(f"retCode=[{retCode}], retMessage=[{retMessage}]")

    print("------------------------------------------")
