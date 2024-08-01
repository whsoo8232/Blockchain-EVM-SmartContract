// scripts/upgrade.js
const { ethers, upgrades } = require("hardhat");

async function main() {
  const MyContractV2 = await ethers.getContractFactory("MyContractV2");
  console.log("Upgrading MyContract...");
  await upgrades.upgradeProxy("<DEPLOYED_CONTRACT_ADDRESS>", MyContractV2);
  console.log("MyContract upgraded to V2");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});