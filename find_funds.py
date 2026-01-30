from web3 import Web3
import requests

# HD HOT WALLET - Consolidated funds vault
HD_HOT_WALLET = '0xf5C649356608F8713c3C2C7d887aD3ad2580e8ce'

# Token contracts
BSC_USDT = '0x55d398326f99059fF775485246999027B3197955'
BSC_USDC = '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d'
TST_TOKEN = '0x4B3ff00Bd27a9d75204CceB619d5B1D393dbaE71'

POLYGON_USDC = '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359'
POLYGON_USDT = '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'

TRON_USDT = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'

ERC20_ABI = [
    {
        'constant': True,
        'inputs': [{'name': '_owner', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'name': 'balance', 'type': 'uint256'}],
        'type': 'function'
    }
]

print('=' * 70)
print('SEARCHING FOR FUNDS - HD_HOT_WALLET')
print(f'Wallet: {HD_HOT_WALLET}')
print('=' * 70)
print()

# BSC Check
print('BSC (BNB Smart Chain)')
print('-' * 70)
try:
    w3_bsc = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org'))
    
    # BNB native
    bnb_balance = w3_bsc.eth.get_balance(HD_HOT_WALLET)
    bnb_amount = w3_bsc.from_wei(bnb_balance, 'ether')
    print(f'  BNB:    {bnb_amount:.8f}')
    
    # USDT
    usdt_contract = w3_bsc.eth.contract(address=BSC_USDT, abi=ERC20_ABI)
    usdt_balance = usdt_contract.functions.balanceOf(HD_HOT_WALLET).call()
    usdt_amount = usdt_balance / 1e18
    print(f'  USDT:   ${usdt_amount:.2f}')
    
    # USDC
    usdc_contract = w3_bsc.eth.contract(address=BSC_USDC, abi=ERC20_ABI)
    usdc_balance = usdc_contract.functions.balanceOf(HD_HOT_WALLET).call()
    usdc_amount = usdc_balance / 1e18
    print(f'  USDC:   ${usdc_amount:.2f}')
    
    # TST
    tst_contract = w3_bsc.eth.contract(address=TST_TOKEN, abi=ERC20_ABI)
    tst_balance = tst_contract.functions.balanceOf(HD_HOT_WALLET).call()
    tst_amount = tst_balance / 1e18
    print(f'  TST:    {tst_amount:.2f}')
    
except Exception as e:
    print(f'  ERROR: {str(e)}')

print()

# Polygon Check
print('POLYGON')
print('-' * 70)
try:
    w3_polygon = Web3(Web3.HTTPProvider('https://polygon-mainnet.g.alchemy.com/v2/a-dy4J4WsLejZXeEHWtnB'))
    
    # MATIC native
    matic_balance = w3_polygon.eth.get_balance(HD_HOT_WALLET)
    matic_amount = w3_polygon.from_wei(matic_balance, 'ether')
    print(f'  MATIC:  {matic_amount:.8f}')
    
    # USDC
    usdc_contract = w3_polygon.eth.contract(address=POLYGON_USDC, abi=ERC20_ABI)
    usdc_balance = usdc_contract.functions.balanceOf(HD_HOT_WALLET).call()
    usdc_amount = usdc_balance / 1e6
    print(f'  USDC:   ${usdc_amount:.2f}')
    
    # USDT
    usdt_contract = w3_polygon.eth.contract(address=POLYGON_USDT, abi=ERC20_ABI)
    usdt_balance = usdt_contract.functions.balanceOf(HD_HOT_WALLET).call()
    usdt_amount = usdt_balance / 1e6
    print(f'  USDT:   ${usdt_amount:.2f}')
    
except Exception as e:
    print(f'  ERROR: {str(e)}')

print()

# TRON Check
print('TRON')
print('-' * 70)
try:
    # Check TRX balance
    tron_wallet_base58 = HD_HOT_WALLET  # We'll need to convert this properly
    # For now, just try direct API call
    headers = {'Accept': 'application/json'}
    tron_url = f'https://api.trongrid.io/v1/accounts/{tron_wallet_base58}'
    response = requests.get(tron_url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            trx_balance_sun = data['data'][0].get('balance', 0)
            trx_amount = trx_balance_sun / 1e6
            print(f'  TRX:    {trx_amount:.6f}')
            
            # Check USDT on TRON
            trc20_balance = data['data'][0].get('trc20', [])
            print(f'  USDT (TRON): Checking...')
        else:
            print(f'  Account not found on TRON')
    else:
        print(f'  TRON API Error: {response.status_code}')
        
except Exception as e:
    print(f'  ERROR: {str(e)}')

print()
print('=' * 70)
print('Note: HD_HOT_WALLET is EVM-compatible (works on BSC, Polygon)')
print('      Need TRON address conversion for TRON network check')
print('=' * 70)
