from web3 import Web3
import requests

# BSC
bsc_rpc = 'https://bsc-dataseed1.binance.org'
bsc_wallet = '0x571E52efc50055d760CEaE2446aE3B469a806279'

# Polygon
polygon_rpc = 'https://polygon-mainnet.g.alchemy.com/v2/a-dy4J4WsLejZXeEHWtnB'
polygon_wallet = '0x571E52efc50055d760CEaE2446aE3B469a806279'

# TRON
tron_wallet = 'TJxZwQtPxj9y3KSa7KQUdQjsBzEsEt9Xiu'

print('=' * 60)
print('WALLET BALANCE CHECK')
print('=' * 60)

# BSC
try:
    w3_bsc = Web3(Web3.HTTPProvider(bsc_rpc))
    bsc_balance = w3_bsc.eth.get_balance(bsc_wallet)
    bsc_balance_bnb = w3_bsc.from_wei(bsc_balance, 'ether')
    print(f'\nBSC (BNB Smart Chain)')
    print(f'  Wallet: {bsc_wallet}')
    print(f'  Balance: {bsc_balance_bnb:.8f} BNB')
except Exception as e:
    print(f'\nBSC Error: {str(e)}')

# Polygon
try:
    w3_polygon = Web3(Web3.HTTPProvider(polygon_rpc))
    polygon_balance = w3_polygon.eth.get_balance(polygon_wallet)
    polygon_balance_matic = w3_polygon.from_wei(polygon_balance, 'ether')
    print(f'\nPOLYGON')
    print(f'  Wallet: {polygon_wallet}')
    print(f'  Balance: {polygon_balance_matic:.8f} MATIC')
except Exception as e:
    print(f'\nPOLYGON Error: {str(e)}')

# TRON
try:
    tron_url = f'https://api.trongrid.io/v1/accounts/{tron_wallet}'
    response = requests.get(tron_url, headers={'Accept': 'application/json'})
    data = response.json()
    
    if 'data' in data and len(data['data']) > 0:
        tron_balance_sun = data['data'][0].get('balance', 0)
        tron_balance_trx = tron_balance_sun / 1e6
        print(f'\nTRON')
        print(f'  Wallet: {tron_wallet}')
        print(f'  Balance: {tron_balance_trx:.6f} TRX')
    else:
        print(f'\nTRON')
        print(f'  Wallet: {tron_wallet}')
        print(f'  Balance: Account not found (0 TRX)')
except Exception as e:
    print(f'\nTRON Error: {str(e)}')

print('\n' + '=' * 60)
