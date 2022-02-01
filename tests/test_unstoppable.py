from brownie import accounts,DamnValuableToken,UnstoppableLender,ReceiverUnstoppable,exceptions
import pytest
from web3 import Web3

TOKENS_IN_POOL = Web3.toWei(1000000, "ether")
INITIAL_ATTACKER_BALANCE = Web3.toWei(100, "ether")


def test_stopLoan():
    deployer = accounts[0]
    attacker = accounts[1]
    someUser = accounts[2]
    token = DamnValuableToken.deploy({"from": deployer})
    pool = UnstoppableLender.deploy(token.address, {"from": deployer})

    token.approve(pool.address, TOKENS_IN_POOL, {"from": deployer})
    pool.depositTokens(TOKENS_IN_POOL, {"from": deployer})
    token.transfer(attacker, INITIAL_ATTACKER_BALANCE, {"from": deployer})
    assert token.balanceOf(pool.address) == TOKENS_IN_POOL
    assert token.balanceOf(attacker.address) == INITIAL_ATTACKER_BALANCE
    
    receiveContract = ReceiverUnstoppable.deploy(pool.address, {"from": someUser})
    receiveContract.executeFlashLoan(10, {"from": someUser})

    # YOUR EXPLOIT GOES HERE

    # SUCCESS CONDITION
    with pytest.raises(exceptions.VirtualMachineError):
        receiveContract.executeFlashLoan(10, {"from": someUser})
