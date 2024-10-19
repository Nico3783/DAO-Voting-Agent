# import logging
from theoriq import Agent, AgentConfig
from proposals import fetch_active_proposals
from analyze import analyze_proposals, chat_with_openai_conversational  # Import the OpenAI function for conversation
from web3_integration import connect_to_web3, get_wallet_balance, cast_vote, get_user_inputs
from logging_config import setup_logger

# Set up logging
logger = setup_logger()

agent = Agent(AgentConfig.from_env())


def handle_new_proposal(proposal, web3, user_wallet_address, contract_address, abi):
    """
    Handles new proposals, fetches wallet balance, analyzes proposals, and casts votes.
    """
    logger.info(f"Handling new proposal: {proposal['title']}")

    try:
        # Fetch wallet balance
        balance = get_wallet_balance(web3, user_wallet_address)
        logger.info(f"Wallet Balance for {user_wallet_address}: {balance} ETH")

        # Analyze the proposal
        recommendation = analyze_proposals()
        logger.info(f"Recommendation for proposal '{proposal['title']}': {recommendation}")

        # Optionally cast a vote on a proposal if conditions are met
        if recommendation == 'Approve':
            logger.info(f"Casting 'yes' vote for proposal ID: {proposal['id']}")
            cast_vote(web3, user_wallet_address, contract_address, abi, proposal['id'], 'yes')
        else:
            logger.info(f"Casting 'no' vote for proposal ID: {proposal['id']}")
            cast_vote(web3, user_wallet_address, contract_address, abi, proposal['id'], 'no')

        return (f"**Proposal:** {proposal['title']}\n**Wallet Balance:** {balance} ETH"
                f"\n**Recommendation:** {recommendation}")

    except Exception as e:
        logger.error(f"Error handling proposal '{proposal['title']}': {e}")
        return f"An error occurred while handling the proposal: {proposal['title']}"


def handle_openai_queries(user_input, web3, user_wallet_address):
    """
    Handles OpenAI queries related to wallet balance and other conversational inputs.
    """
    try:
        if "wallet balance" in user_input.lower():
            balance = get_wallet_balance(web3, user_wallet_address)
            logger.info(f"Responded to wallet balance query. Balance: {balance} ETH")
            return f"Your wallet balance is: {balance} ETH"
        else:
            # For other OpenAI conversational queries
            response = chat_with_openai_conversational(user_input)
            logger.info(f"Responded to OpenAI conversational query: {user_input}")
            return response

    except Exception as e:
        logger.error(f"Error handling OpenAI query '{user_input}': {e}")
        return "An error occurred while processing your request."


def run_agent():
    """
    Main function to run the agent, connect to Web3, fetch proposals, and handle them.
    """
    try:
        logger.info("Starting agent...")

        # Get user inputs directly from web3_integration
        user_inputs = get_user_inputs()
        infura_url = user_inputs['infura_url']
        wallet_address = user_inputs['wallet_address']
        contract_address = user_inputs['contract_address']
        abi = user_inputs['abi']

        # Establish Web3 connection
        web3 = connect_to_web3(infura_url)
        logger.info(f"Connected to Web3 via Infura URL: {infura_url}")

        # Fetch active proposals
        proposals = fetch_active_proposals()
        logger.info(f"Fetched {len(proposals)} active proposals.")

        # Handle each proposal
        for proposal in proposals:
            response = handle_new_proposal(proposal, web3, wallet_address, contract_address, abi)
            logger.info(f"Handled proposal: {response}")

        # Start interactive session for OpenAI
        analyze_proposals()
        logger.info("Interactive OpenAI session started.")
        print("Start interacting with your DAO Voting Agent. Type 'exit' to stop.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Goodbye!")
                logger.info("Agent session ended by user.")
                break
            openai_response = handle_openai_queries(user_input, web3, wallet_address)
            print(f"DAO Agent: {openai_response}")

    except Exception as e:
        logger.error(f"Error during agent execution: {e}")
        print("An error occurred while running the agent.")


if __name__ == "__main__":
    run_agent()
