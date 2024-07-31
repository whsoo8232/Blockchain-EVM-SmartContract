const { ethers, upgrades } = require("hardhat");
const { verify } = require("../utils/verify");
const { BigNumber } = ethers;

async function main() {
  const UpgradableV1 = await ethers.getContractFactory("ARTC");


  console.log("Deploying ARTC...");
  const contract = await upgrades.deployProxy(UpgradableV1, [], {
    initializer: "initialize",
    kind: "transparent",
  });
  await contract.deployed();
  console.log("ARTC deployed address to:", contract.address);
}

main();
