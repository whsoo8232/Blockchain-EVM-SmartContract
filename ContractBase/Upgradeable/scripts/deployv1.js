const { ethers, upgrades } = require("hardhat");
const { verify } = require("../utils/verify");
const { BigNumber } = ethers;

async function main() {
  const UpgradableV1 = await ethers.getContractFactory("awdawd");


  console.log("Deploying awdawd...");
  const contract = await upgrades.deployProxy(UpgradableV1, [], {
    initializer: "initialize",
    kind: "transparent",
  });
  await contract.deployed();
  console.log("awdawd deployed address to:", contract.address);
}

main();
