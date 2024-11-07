# import logging
import os

import openai
from dotenv import load_dotenv
from web3 import Web3

from src.proposals import fetch_active_proposals
from src.web3_integration import get_user_inputs, get_wallet_balance
from src.logging_config import setup_logger

# Set up logging
logger = setup_logger()

# Load environment variables
load_dotenv()


# Ensure OpenAI API key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is missing.")
openai.api_key = OPENAI_API_KEY

# Initialize conversation history with a system prompt
conversation_history = [{"role": "system", "content": "You are an assistant helping with DAO voting."}]


# Function to handle conversation
def chat_with_openai_conversational(prompt):
    """
    Sends the user's prompt to OpenAI and maintains conversation history.
    """
    logger.info(f"Received user prompt: {prompt}")

    # Add user's input to conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Get the response from OpenAI's chat completion
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Specifically for GPT-4o mini
        messages=conversation_history,
        max_tokens=300,
        temperature=0.7
    )

    # Extract and log the response from OpenAI
    message = response['choices'][0]['message']['content'].strip()
    logger.info(f"Received response from OpenAI: {message}")

    # Add OpenAI's response to conversation history
    conversation_history.append({"role": "assistant", "content": message})
    return message


# Function to analyze project status
def analyze_project_status(proposals, project_data, wallet_balance):
    """
    Generate a detailed response to the user based on the project status, proposals, and OpenAI integration.
    """
    if not proposals:
        base_response = "It seems like there are currently no active proposals for your DAO voting project."
    else:
        base_response = f"There are {len(proposals)} active proposals available. Let's go over them: {proposals}"

    logger.info(f"Base response prepared: {base_response}")

    prompt = f"""
    You are an AI assistant helping with a DAO voting project. 
    The project involves interacting with smart contracts, casting votes, and analyzing on-chain proposals. 
    The current status of the project is as follows:

    {base_response}

    The project's important variables are:
    - Infura URL: {project_data['infura_url']}
    - Contract Address: {project_data['contract_address']}
    - ABI: {project_data['abi']}
    - Wallet Address: {project_data['wallet_address']}
    - Wallet Balance: {wallet_balance} ETH

    Can you give feedback on the project (not more than 2048 array of response) and let me know if anything is missing or incorrect?
    (Remember NOT to use bold format for your response, 
    and do well to respond to users politely and don't address them as the project owner but strictly as users,
    and ensure NOT to mention that You're trained by OpenAI, just be a polite Assistant.)
    """

    openai_response = chat_with_openai_conversational(prompt)
    return openai_response


# Function for interactive conversation loop
def interactive_conversation():
    """
    Starts a continuous conversation loop with the user.
    """
    print("Start interacting with your DAO Voting Agent. "
          "Type 'exit' to stop or say 'provide inputs again' to re-enter inputs.")
    logger.info("Interactive conversation started.")

    while True:
        user_input = input("You: ")
        user_inputs = get_user_inputs()
        infura_url = user_inputs['infura_url']
        web3 = Web3(Web3.HTTPProvider(infura_url))

        if not web3.is_connected():
            logger.error("Unable to connect to Infura.")
            raise Exception("Unable to connect to Infura.")

        if user_input.lower() == 'provide inputs again':
            logger.info("User requested to re-enter inputs.")
            print("Sure! Let's re-enter your inputs.")
            return  # Exit the conversation loop to re-enter inputs

        if user_input.lower() == 'exit':
            logger.info("User exited the conversation.")
            print("Goodbye and have a nice time!")
            break  # Quit the conversation normally

        # Fetch OpenAI's response
        response = chat_with_openai_conversational(user_input)
        print(f"DAO Agent: {response}")


# Function to check wallet balance
def check_wallet_balance(web3, wallet_address):
    """
    Check and return the wallet balance in ETH.
    """
    logger.info(f"Checking wallet balance for address: {wallet_address}")
    balance_wei = web3.eth.get_balance(wallet_address)
    balance_eth = web3.from_wei(balance_wei, 'ether')
    logger.info(f"Wallet balance: {balance_eth} ETH")
    return balance_eth


# Main proposal analysis function
def analyze_proposals():
    """
    Analyze proposals and generate a chat-like response using OpenAI.
    """
    try:
        logger.info("Starting proposal analysis process.")

        # Get user inputs from web3_integration
        user_inputs = get_user_inputs()
        contract_address = user_inputs['contract_address']
        abi = user_inputs['abi']
        infura_url = user_inputs['infura_url']
        wallet_address = user_inputs['wallet_address']

        # Initialize Web3 with Infura URL
        web3 = Web3(Web3.HTTPProvider(infura_url))
        if not web3.is_connected():
            logger.error("Unable to connect to Infura.")
            raise Exception("Unable to connect to Infura.")

        # Fetch wallet balance
        wallet_balance = check_wallet_balance(web3, wallet_address)

        # Fetch active proposals using the new function from proposals.py
        proposals = fetch_active_proposals()

        # Define the project's important data to analyze
        project_data = {
            'infura_url': infura_url,
            'contract_address': contract_address,
            'abi': abi,
            'wallet_address': wallet_address
        }

        # Use OpenAI to analyze and provide interactive feedback
        response = analyze_project_status(proposals, project_data, wallet_balance)
        logger.info(f"DAO Agent: {response}")
        print(f"DAO Agent: {response}")

        # Start an interactive conversation loop
        interactive_conversation()

    except Exception as e:
        logger.error(f"Error during proposal analysis: {str(e)}")
        user_inputs = get_user_inputs()

        infura_url = user_inputs['infura_url']
        wallet_address = user_inputs['wallet_address']

        # Initialize Web3 with Infura URL
        web3 = Web3(Web3.HTTPProvider(infura_url))
        if not web3.is_connected():
            logger.error("Unable to connect to Infura.")
            raise Exception("Unable to connect to Infura.")

        # Handle any errors and send them to OpenAI for response
        error_message = f"An error occurred while analyzing proposals: {str(e)}"
        prompt = f"""
        You are an AI assistant helping with a DAO voting project. An error occurred during the process:
        {error_message}

        Can you explain this error and suggest steps to resolve it? (not more than 2048 array of response)
        (Remember NOT to use bold format for your response, 
        and do well to respond to users politely and don't address them as the project owner but strictly as users,
        and ensure NOT to mention that You're trained by OpenAI, just be a polite Assistant.)
        """
        # Check if the user asks about wallet balance
        if "wallet balance" in prompt.lower():
            balance = get_wallet_balance(web3, wallet_address)
            response = f"Your wallet balance is {balance} ETH."
            return response  # Directly return balance without calling OpenAI

        # Send error response via OpenAI
        error_response = chat_with_openai_conversational(prompt)
        logger.error(f"Error response from OpenAI: {error_response}")
        print(error_response)


if __name__ == "__main__":
    analyze_proposals()
