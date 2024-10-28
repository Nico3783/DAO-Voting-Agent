from .web3_integration import get_wallet_balance, cast_vote, connect_to_web3, get_user_inputs
from .proposals import fetch_active_proposals
from .agent import handle_new_proposal
from .analyze import analyze_proposals
from .logging_config import setup_logger

# Set up logging
logger = setup_logger()


def extract_proposal_id(user_query):
    """
    Extracts the proposal ID from the query string.
    """
    words = user_query.split()
    for i, word in enumerate(words):
        if word.lower() == "proposal" and i + 1 < len(words):
            proposal_id = words[i + 1]
            logger.info(f"Extracted proposal ID: {proposal_id}")
            return proposal_id
    logger.warning("No proposal ID found in the query.")
    return None


def extract_vote_choice(user_query):
    """
    Extracts the vote choice ('for', 'against', or 'abstain') from the query string.
    """
    vote_keywords = {
        "for": "yes",
        "against": "no",
        "abstain": "abstain"
    }

    query_lower = user_query.lower()
    for keyword, vote in vote_keywords.items():
        if keyword in query_lower:
            logger.info(f"Vote choice extracted: {vote} (based on keyword '{keyword}')")
            return vote

    logger.error("Invalid vote choice. Please specify 'for', 'against', or 'abstain'.")
    raise ValueError("Invalid vote choice. Please specify 'for', 'against', or 'abstain'.")


def on_user_query(user_query):
    """
    Responds to user queries about proposals, balance, and casting votes.
    """
    logger.info(f"User query received: {user_query}")

    # Getting the necessary user inputs from web3_integration
    user_inputs = get_user_inputs()
    infura_url = user_inputs['infura_url']
    wallet_address = user_inputs['wallet_address']
    contract_address = user_inputs['contract_address']
    abi = user_inputs['abi']

    # Establishing Web3 connection
    try:
        web3 = connect_to_web3(infura_url)
        logger.info(f"Connected to Web3 with Infura URL: {infura_url}")
    except Exception as e:
        logger.error(f"Error connecting to Web3: {e}")
        return

    if "proposal" in user_query.lower():
        try:
            logger.info("Fetching active proposals...")
            proposals = fetch_active_proposals()
            if proposals:
                logger.info(f"{len(proposals)} proposals fetched successfully.")
                for proposal in proposals:
                    response = handle_new_proposal(proposal, web3, wallet_address, contract_address, abi)
                    logger.info(f"Response: {response}")
            else:
                logger.warning("No active proposals found.")
        except Exception as e:
            logger.error(f"Error fetching proposals: {e}")

    elif "balance" in user_query.lower():
        try:
            logger.info(f"Fetching balance for wallet: {wallet_address}")
            balance = get_wallet_balance(web3, wallet_address)
            logger.info(f"Wallet balance: {balance} ETH")
        except Exception as e:
            logger.error(f"Error fetching wallet balance: {e}")

    elif "vote" in user_query.lower():
        try:
            # Extract proposal ID and vote choice from user query
            proposal_id = extract_proposal_id(user_query)
            vote_choice = extract_vote_choice(user_query)

            if proposal_id and vote_choice:
                logger.info(f"Casting vote for proposal ID {proposal_id} with choice {vote_choice}")
                cast_vote(web3, wallet_address, contract_address, abi, proposal_id, vote_choice)
                logger.info(f"Vote successfully cast for proposal {proposal_id}.")
            else:
                logger.warning("Could not determine proposal ID or vote choice from query.")
        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
        except Exception as e:
            logger.error(f"Unexpected error casting vote: {e}")
    else:
        logger.warning("Unrecognized query. I can help you with DAO voting strategies. "
                       "Ask me about active proposals or your wallet balance!")
    analyze_proposals()


# Test the on_user_query function
if __name__ == "__main__":
    test_query = input("Enter your query: ")
    on_user_query(test_query)
