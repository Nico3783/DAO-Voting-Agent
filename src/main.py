import os
import openai
from theoriq import Agent, AgentConfig
from theoriq.biscuit import TheoriqCost
from theoriq.execute import ExecuteContext, ExecuteRequestBody, ExecuteResponse
from theoriq.schemas import DialogItem, TextItemBlock
from theoriq.types import Currency
# from src.app import app

from src.analyze import (analyze_proposals, analyze_project_status, chat_with_openai_conversational,
                         interactive_conversation)
from src.proposals import fetch_active_proposals
from src.web3_integration import connect_to_web3, get_wallet_balance, cast_vote, get_user_inputs
from src.logging_config import setup_logger

# Set up logging (using the centralized logger from logging_config)
logger = setup_logger()

# Initialize OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OpenAI API key is missing.")
    raise ValueError("OpenAI API key is missing.")
openai.api_key = OPENAI_API_KEY

# Initialize Theoriq agent configuration from environment
agent = Agent(AgentConfig.from_env())


def get_openai_response(prompt):
    """Generate OpenAI response based on the input prompt."""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logger.error(f"Error generating OpenAI response: {str(e)}")
        return f"Error generating OpenAI response: {str(e)}"


def handle_new_proposal(proposal, web3, user_wallet_address, contract_address, abi):
    """Process and analyze a new proposal, including casting a vote if applicable."""
    logger.info(f"Handling new proposal: {proposal['title']}")

    # Fetch wallet balance
    balance = get_wallet_balance(web3, user_wallet_address)
    logger.info(f"Wallet Balance for {user_wallet_address}: {balance} ETH")

    # Analyze proposal and determine voting recommendation
    recommendation = analyze_proposals()
    logger.info(f"Recommendation for proposal '{proposal['title']}': {recommendation}")

    # Cast vote based on recommendation
    vote_choice = 'yes' if recommendation == 'Approve' else 'no'
    logger.info(f"Casting '{vote_choice}' vote for proposal ID: {proposal['id']}")
    cast_vote(web3, user_wallet_address, contract_address, abi, proposal['id'], vote_choice)

    return f"**Proposal:** {proposal['title']}\n**Wallet Balance:** {balance} ETH\n**Recommendation:** {recommendation}"


def handle_openai_queries(user_input, web3, user_wallet_address, submitted_proposals):
    """Manage OpenAI conversational responses related to wallet balance and proposals."""
    logger.info(f"Received OpenAI query: {user_input}")

    if "wallet balance" in user_input.lower():
        balance = get_wallet_balance(web3, user_wallet_address)
        return f"Your wallet balance is: {balance} ETH"
    elif "show my proposals" in user_input.lower():
        return f"Here are your submitted proposals: {submitted_proposals}" \
            if submitted_proposals else "You have no submitted proposals at the moment."

    # For other conversational queries
    return chat_with_openai_conversational(user_input)


def execute_dao_voting_assistant(user_input):
    """Process DAO voting input through OpenAI and return response."""
    logger.info(f"Executing DAO Voting Assistant with user input: {user_input}")
    prompt = f"Analyze the following user input for DAO voting: {user_input}"
    openai_response = get_openai_response(prompt)

    dialog_item = DialogItem.new_text(
        source="DAO Voting Agent",
        text=f"Welcome to the DAO Voting Assistant.\nOpenAI analysis: {openai_response}"
    )
    return ExecuteResponse(
        dialog_item=dialog_item,
        cost=TheoriqCost.zero(Currency.USDC),
        status_code=200
    )


def run_agent():
    """Main agent function to initialize, fetch proposals, analyze status, and interact with the user."""
    try:
        logger.info("Starting DAO Voting Agent...")

        # Gather user and web3 configuration inputs
        user_inputs = get_user_inputs()
        contract_address, abi, infura_url, wallet_address = (user_inputs['contract_address'],
                                                             user_inputs['abi'],
                                                             user_inputs['infura_url'],
                                                             user_inputs['wallet_address'])

        # Initialize Web3 connection
        web3 = connect_to_web3(infura_url)
        if not web3.is_connected():
            logger.error("Unable to connect to Ethereum Network provider.")
            raise Exception("Unable to connect to Ethereum Network provider.")

        # Fetch wallet balance and active proposals
        wallet_balance = get_wallet_balance(web3, wallet_address)
        proposals = fetch_active_proposals()

        # Define and analyze project data
        project_data = {
            'infura_url': infura_url,
            'contract_address': contract_address,
            'abi': abi,
            'wallet_address': wallet_address
        }
        response = analyze_project_status(proposals, project_data, wallet_balance)
        logger.info(f"DAO Agent: {response}")
        print(f"DAO Agent: {response}")

        # Start interactive conversation
        interactive_conversation()

    except Exception as e:
        logger.error(f"Error in running the agent: {str(e)}")
        handle_agent_error(e)


def handle_agent_error(error):
    """Generate an OpenAI response for an error encountered during the agent's execution."""
    error_message = f"An error occurred while running the agent: {str(error)}"
    prompt = f"""
    (Remember NOT TO use bold text format for your response)
    You are an AI assistant helping with a DAO voting project. An error occurred during the process:
    {error_message}

    Can you explain this error and suggest steps to resolve it? (Remember NOT to use bold format for your response, 
    and do well to respond to users politely and don't address them as the project owner but strictly as users,
    and ensure NOT to mention that You're trained by OpenAI, just be a polite Assistant.)
    """
    error_response = chat_with_openai_conversational(prompt)
    logger.error(f"Error response from OpenAI: {error_response}")
    print(error_response)


def run_agent_theoriq(context: ExecuteContext, request_body: ExecuteRequestBody) -> ExecuteResponse:
    """Theoriq-compliant agent execution function."""
    try:
        logger.info(f"Received request: {context.request_id}")

        # Process user input and generate OpenAI response
        last_block = request_body.last_item.blocks[0]
        text_value = last_block.data.text
        logger.info(f"Processing user input: {text_value}")

        openai_response = chat_with_openai_conversational(text_value)
        response_text = f"Hello {text_value} from a Theoriq Agent! Analysis: {openai_response}"

        return context.new_response(
            blocks=[TextItemBlock(text=response_text)],
            cost=TheoriqCost(amount=1, currency=Currency.USDC)
        )
    except Exception as e:
        logger.error(f"Error in running the agent: {str(e)}")
        return context.new_response(
            blocks=[TextItemBlock(text=f"An error occurred: {str(e)}")],
            cost=TheoriqCost.zero(Currency.USDC)
        )


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8000)
    run_agent()
