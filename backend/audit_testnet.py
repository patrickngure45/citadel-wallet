
from web3 import Web3

# BSC TESTNET
RPC_URL = "https://data-seed-prebsc-1-s1.binance.org:8545/"
USER_0 = "0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce"
USER_1 = "0x578FC7311a846997dc99bF2d4C651418DcFe309A"

def check_bal():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("RPC Connection Failed")
        return

    bal_wei = w3.eth.get_balance(USER_0)
    bal_bnb = w3.from_wei(bal_wei, 'ether')
    print(f"Chain: BSC TESTNET")
    print(f"User 0 (Index 0): {USER_0}")
    print(f"Balance: {bal_bnb} BNB")

    bal_wei_1 = w3.eth.get_balance(USER_1)
    bal_bnb_1 = w3.from_wei(bal_wei_1, 'ether')
    print(f"User 1 (Index 1): {USER_1}")
    print(f"Balance: {bal_bnb_1} BNB")


if __name__ == "__main__":
    check_bal()
