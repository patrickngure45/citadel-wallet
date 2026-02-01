from web3 import Web3

RPC_URL = "https://data-seed-prebsc-1-s1.binance.org:8545/"
ADMIN_ADDRESS = "0x571E52efc50055d760CEaE2446aE3B469a806279"
TST_ADDRESS = "0x297aB5E3Cd7798cC5cA75F30fa06e695F4E954f5"

def check_tst_transfer():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=TST_ADDRESS, abi=[
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}
    ])
    
    bal_wei = contract.functions.balanceOf(ADMIN_ADDRESS).call()
    bal_tst = w3.from_wei(bal_wei, 'ether')
    print(f"Admin TST Balance: {bal_tst}")

if __name__ == "__main__":
    check_tst_transfer()