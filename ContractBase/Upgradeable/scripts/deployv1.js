const { ethers, upgrades } = require("hardhat");
const { verify } = require("../utils/verify");
const { BigNumber } = ethers;

async function main() {
  const UpgradableV1 = await ethers.getContractFactory("TestV1");


  console.log("Deploying TestV1...");
  const contract = await upgrades.deployProxy(UpgradableV1, [], {
    initializer: "initialize",
    kind: "transparent",
  });
  await contract.deployed();
  console.log("TestV1 deployed address to:", contract.address);
}

main();
