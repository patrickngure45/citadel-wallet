from eth_account import Account
from web3 import Web3
from app.core.config import settings

class WalletService:
    def __init__(self):
        self.master_mnemonic = settings.CITADEL_MASTER_SEED
        # Enable Mnemonic features
        Account.enable_unaudited_hdwallet_features()
        
        # Initialize Web3 Connections
        self.w3_eth = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
        self.w3_bsc = Web3(Web3.HTTPProvider(settings.BSC_RPC_URL))
        self.w3_poly = Web3(Web3.HTTPProvider(settings.POLYGON_RPC_URL))
        # BSC Testnet for development
        self.w3_bsc_testnet = Web3(Web3.HTTPProvider("https://data-seed-prebsc-1-s1.binance.org:8545/"))

    def generate_evm_address(self, index: int) -> dict:
        """
        Derives an EVM address (ETH, BSC, MATIC) from the master seed at a specific index.
        Path used: m/44'/60'/0'/0/{index}
        """
        # Standard BIP44 Path for Ethereum: m/44'/60'/0'/0/index
        path = f"m/44'/60'/0'/0/{index}"
        
        # Derive account
        acct = Account.from_mnemonic(self.master_mnemonic, account_path=path)
        
        return {
            "address": acct.address,
            "private_key": acct.key.hex(), # NEVER STORE THIS IN DB. This is just for runtime signing.
            "path": path
        }
    
    async def get_balance(self, address: str, chain: str) -> float:
        """
        Fetches native balance for a given address and chain.
        Returns balance in major units (ETH, BNB, MATIC).
        """
        try:
            if chain.lower() == "ethereum":
                w3 = self.w3_eth
            elif chain.lower() == "bsc":
                w3 = self.w3_bsc
            elif chain.lower() == "polygon":
                w3 = self.w3_poly
            else:
                return 0.0

            if not w3.is_connected():
                return 0.0

            # Web3.py is sync by default, but in async FastAPI endpoints we might block the loop.
            # ideally run in threadpool, but for low traffic MVP direct call is okay, 
            # or we use async web3 provider. For now, keep it simple.
            balance_wei = w3.eth.get_balance(w3.to_checksum_address(address))
            return float(w3.from_wei(balance_wei, 'ether'))
        except Exception as e:
            print(f"Error fetching balance for {chain}: {e}")
            return 0.0

    def get_token_balance(self, address: str, contract_address: str, chain: str) -> float:
        """
        Fetches ERC20 token balance.
        """
        try:
            if chain.lower() == "polygon":
                w3 = self.w3_poly
            elif chain.lower() == "bsc":
                w3 = self.w3_bsc
            elif chain.lower() == "bsc_testnet":
                w3 = self.w3_bsc_testnet
            else:
                return 0.0
            
            abi = [
                {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
            ]
            
            contract = w3.eth.contract(address=w3.to_checksum_address(contract_address), abi=abi)
            raw_balance = contract.functions.balanceOf(w3.to_checksum_address(address)).call()
            decimals = 18 # Default
            try:
                decimals = contract.functions.decimals().call()
            except:
                pass
                
            return raw_balance / (10 ** decimals)
        except Exception as e:
            print(f"Error fetching token balance: {e}")
            return 0.0

    async def transfer_native(self, from_index: int, to_address: str, amount: float, chain: str) -> str:
        """
        Transfers native currency (ETH, BNB, MATIC) from a derived wallet.
        """
        if chain.lower() == "bsc":
            w3 = self.w3_bsc
            chain_id = 56
        elif chain.lower() == "polygon":
            w3 = self.w3_poly
            chain_id = 137
        else:
            raise ValueError(f"Chain {chain} not supported for transfer yet")

        # 1. Get Wallet
        wallet = self.generate_evm_address(from_index)
        sender = w3.to_checksum_address(wallet["address"])
        receiver = w3.to_checksum_address(to_address)
        
        # 2. Prepare Transaction
        nonce = w3.eth.get_transaction_count(sender)
        gas_price = w3.eth.gas_price
        
        tx = {
            'nonce': nonce,
            'to': receiver,
            'value': w3.to_wei(amount, 'ether'),
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': chain_id
        }
        
        # 3. Sign & Send
        signed_tx = w3.eth.account.sign_transaction(tx, wallet["private_key"])
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return w3.to_hex(tx_hash)

    async def sweep_native(self, from_index: int, to_address: str, chain: str) -> str:
        """
        Automatically empties a wallet into the target address (calculating gas fees).
        Returns TX Hash or None if balance is too low.
        """
        if chain.lower() == "bsc":
            w3 = self.w3_bsc
            chain_id = 56
        elif chain.lower() == "polygon":
            w3 = self.w3_poly
            chain_id = 137
        else:
            return None

        # 1. Get Wallet & Balance
        wallet = self.generate_evm_address(from_index)
        sender = w3.to_checksum_address(wallet["address"])
        receiver = w3.to_checksum_address(to_address)
        
        balance_wei = w3.eth.get_balance(sender)
        gas_price = w3.eth.gas_price
        gas_limit = 21000
        cost_wei = gas_limit * gas_price
        
        # Buffer to ensure tx doesn't fail due to fluctuation (1.1x cost)
        safe_cost = int(cost_wei * 1.1)

        if balance_wei <= safe_cost:
            return f"Skipped: Balance ({w3.from_wei(balance_wei, 'ether'):.6f}) too low for gas ({w3.from_wei(safe_cost, 'ether'):.6f})"

        amount_to_send_wei = balance_wei - cost_wei

        # 2. Send
        tx = {
            'nonce': w3.eth.get_transaction_count(sender),
            'to': receiver,
            'value': amount_to_send_wei,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': chain_id
        }
        
        signed_tx = w3.eth.account.sign_transaction(tx, wallet["private_key"])
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return w3.to_hex(tx_hash)

    async def transfer_token(self, from_index: int, to_address: str, token_address: str, chain: str) -> str:
        """
        Transfers FULL token balance from a derived wallet to target.
        """
        if chain.lower() == "bsc":
            w3 = self.w3_bsc
            chain_id = 56
        elif chain.lower() == "polygon":
            w3 = self.w3_poly
            chain_id = 137
        else:
            return None

        # 1. Setup
        wallet = self.generate_evm_address(from_index)
        sender = w3.to_checksum_address(wallet["address"])
        receiver = w3.to_checksum_address(to_address)
        token_contract_addr = w3.to_checksum_address(token_address)
        
        erc20_abi = [
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
            {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
        ]
        
        contract = w3.eth.contract(address=token_contract_addr, abi=erc20_abi)
        
        # 2. Check Balance
        token_balance = contract.functions.balanceOf(sender).call()
        if token_balance == 0:
            return None

        # 3. Estimate Gas for Transfer
        # Standard token transfer is ~65,000 gas. Let's be safe with 100k or estimate.
        try:
            gas_estimate = contract.functions.transfer(receiver, token_balance).estimate_gas({'from': sender})
        except:
            gas_estimate = 80000 

        gas_price = w3.eth.gas_price
        required_native_wei = gas_estimate * gas_price
        
        # 4. Check if User has Gas
        user_native_balance = w3.eth.get_balance(sender)
        
        if user_native_balance < required_native_wei:
            return f"NEEDS_GAS:{required_native_wei - user_native_balance}"

        # 5. Execute Transfer
        tx = contract.functions.transfer(receiver, token_balance).build_transaction({
            'chainId': chain_id,
            'gas': gas_estimate,
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(sender),
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, wallet["private_key"])
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return w3.to_hex(tx_hash)

    async def payout_from_master(self, to_address: str, token_address: str, amount: float, chain: str) -> str:
        """
        Sends funds from the MASTER HOT WALLET (Index 0) to a user.
        Used for withdrawals.
        """
        if chain.lower() == "bsc":
            w3 = self.w3_bsc
            chain_id = 56
        elif chain.lower() == "polygon":
            w3 = self.w3_poly
            chain_id = 137
        else:
            raise ValueError("Unsupported Chain")

        # 1. Master Wallet (Index 0)
        master = self.generate_evm_address(0) # Index 0 is the Vault
        sender = w3.to_checksum_address(master["address"])
        receiver = w3.to_checksum_address(to_address)
        token_contract_addr = w3.to_checksum_address(token_address)
        
        # 2. Contract
        erc20_abi = [
            {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
        ]
        contract = w3.eth.contract(address=token_contract_addr, abi=erc20_abi)
        
        # 3. Decimals
        try:
            decimals = contract.functions.decimals().call()
        except:
            decimals = 18
            
        amount_wei = int(amount * (10 ** decimals))

        # 4. Execute
        tx = contract.functions.transfer(receiver, amount_wei).build_transaction({
            'chainId': chain_id,
            'gas': 100000, # Safety buffer
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(sender),
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, master["private_key"])
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return w3.to_hex(tx_hash)

wallet_service = WalletService()
