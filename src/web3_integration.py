from web3 import Web3
from dotenv import load_dotenv
import json
from logging_config import setup_logger  # Import the centralized logger setup

# Set up logging
logger = setup_logger()

load_dotenv()
user_inputs_cache = None


def get_user_inputs():
    """
    Collect all the necessary user inputs at once and return as a dictionary.
    """
    global user_inputs_cache
    if user_inputs_cache is None:
        try:
            # Welcome message and explanation
            print("Welcome to the DAO Voting Agent!")
            print("This agent helps you interact with your DAO for personalized voting and proposal analysis.")
            print("You will need to provide the following information:")
            print("1. DAO Space (e.g., Uniswap)")
            print("2. Contract ABI (as a JSON string)")
            print("3. Contract Address")
            print("4. Infura URL (Ethereum network provider URL)")
            print("5. Wallet Address")

            # Ask for confirmation to proceed
            proceed = input("Do you want to proceed with entering the inputs?"
                            " (Type 'yes' to continue): ").strip().lower()
            if proceed != 'yes':
                print("Exiting input collection.")
                return None

            # Initialize Web3 provider
            web3 = Web3(Web3.HTTPProvider())

            # Collect user inputs
            space = input("Enter the DAO space (e.g. Uniswap): ")
            abi = json.loads(input("Enter the contract ABI (as a JSON string): "))
            contract_address = input("Enter the contract address: ")
            infura_url = input("Enter your Ethereum network provider URL (e.g. Infura URL): ")
            wallet_address = web3.to_checksum_address(input("Enter your wallet address: "))

            # Store the inputs in the cache
            user_inputs_cache = {
                "space": space,
                "abi": abi,
                "contract_address": contract_address,
                "infura_url": infura_url,
                "wallet_address": wallet_address
            }

            logger.info(f"User inputs collected successfully: {user_inputs_cache}")
        except Exception as e:
            logger.error(f"Error while collecting user inputs: {e}")
            raise e
    return user_inputs_cache


def connect_to_web3(infura_url):
    """
    Connect to the Ethereum network using Web3 and Infura URL.
    """
    try:
        web3 = Web3(Web3.HTTPProvider(infura_url))
        if not web3.is_connected():
            logger.error("Failed to connect to Ethereum network.")
            raise Exception("Failed to connect to Ethereum network")
        logger.info(f"Connected to Ethereum network using the provided URL: {infura_url}")
        print("Connection successful!")
        return web3
    except Exception as e:
        logger.error(f"Error while connecting to Ethereum network: {e}")
        raise e


def get_wallet_balance(web3, wallet_address):
    """
    Fetch the wallet balance using the provided wallet address.
    """
    try:
        wallet_address = web3.to_checksum_address(wallet_address)
        balance_wei = web3.eth.get_balance(wallet_address)
        balance_ether = web3.from_wei(balance_wei, 'ether')
        logger.info(f"Fetched wallet balance: {balance_ether} ETH for address {wallet_address}")
        return balance_ether
    except Exception as e:
        logger.error(f"Error while fetching wallet balance: {e}")
        raise e


def cast_vote(web3, account, contract_address, abi, proposal_id, vote_choice):
    """
    Cast a vote on a DAO proposal by interacting with the smart contract.
    """
    try:
        logger.info(f"Attempting to cast vote for proposal ID: {proposal_id} with choice: {vote_choice}")
        contract = web3.eth.Contract(address=contract_address, abi=abi)
        transaction = contract.functions.vote(proposal_id, vote_choice).buildTransaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 2000000,
            'gasPrice': web3.toWei('50', 'gwei'),
        })

        signed_txn = web3.eth.account.sign_transaction(transaction, account.key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f"Vote cast successfully! Transaction hash: {tx_hash.hex()}")
        print(f"Vote cast successfully! Transaction hash: {tx_hash.hex()}")
        return tx_hash.hex()
    except Exception as e:
        logger.error(f"Error while casting vote: {e}")
        raise e


def get_active_onchain_proposals(contract_address, abi):
    """
    Fetch active proposals from the on-chain smart contract for a given DAO space.
    """
    try:
        web3 = Web3(Web3.HTTPProvider())
        contract = web3.eth.contract(address=contract_address, abi=abi)
        proposals = contract.functions.getActiveProposals().call()
        logger.info(f"Active proposals fetched successfully: {proposals}")
        print(f"Active proposals fetched: {proposals}")
        return proposals
    except Exception as e:
        logger.error(f"Error while fetching active proposals: {e}")
        raise Exception(f"Error fetching active proposals: {e}")
