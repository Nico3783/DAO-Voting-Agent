import os
import openai
from theoriq import Agent, AgentConfig
from theoriq.biscuit import TheoriqCost
from theoriq.execute import ExecuteContext, ExecuteRequestBody, ExecuteResponse
from theoriq.schemas import DialogItem
from theoriq.types import Currency

from analyze import analyze_proposals, analyze_project_status, chat_with_openai_conversational, interactive_conversation
from proposals import fetch_active_proposals
from web3_integration import connect_to_web3, get_wallet_balance, cast_vote, get_user_inputs
from logging_config import setup_logger

# Set up logging (using the centralized logger from logging_config)
logger = setup_logger()

# Initializing the agent with config from environment
agent = Agent(AgentConfig.from_env())

# This part is to ensure OpenAI API key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OpenAI API key is missing.")  # logger already assigned the function from logging_config
    raise ValueError("OpenAI API key is missing.")
openai.api_key = OPENAI_API_KEY


def get_openai_response(prompt):
    """
    Function to handle OpenAI response generation.
    """
    try:
        # To make a request to OpenAI's API to generate a response based on the prompt
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
    """
    Handles new proposals, fetches wallet balance, analyzes proposals, and casts votes.
    """
    logger.info(f"Handling new proposal: {proposal['title']}")

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

    return f"**Proposal:** {proposal['title']}\n**Wallet Balance:** {balance} ETH\n**Recommendation:** {recommendation}"


def handle_openai_queries(user_input, web3, user_wallet_address, submitted_proposals):
    """
    Handles OpenAI queries related to wallet balance and other conversational inputs.
    """
    logger.info(f"Received OpenAI query: {user_input}")
    if "wallet balance" in user_input.lower():
        balance = get_wallet_balance(web3, user_wallet_address)
        return f"Your wallet balance is: {balance} ETH"

    elif "show my proposals" in user_input.lower():
        if submitted_proposals:
            return f"Here are your submitted proposals: {submitted_proposals}"
        else:
            return "You have no submitted proposals at the moment."

    # For other conversational queries, requests will be sent to OpenAI
    response = chat_with_openai_conversational(user_input)
    return response


def execute_dao_voting_assistant(user_input):
    """
    Analyzes user input for DAO voting using OpenAI and returns a response.
    """
    logger.info(f"Executing DAO Voting Assistant with user input: {user_input}")

    # Creating the prompt for OpenAI based on the user input
    prompt = f"Analyze the following user input for DAO voting: {user_input}"

    # Generate the OpenAI response based on the user input
    openai_response = get_openai_response(prompt)

    # Return a valid ExecuteResponse
    dialog_item = DialogItem.new_text(  # Using new_text method to create a valid DialogItem
        source="DAO Voting Agent",
        text=f"Welcome to the DAO Voting Assistant.\nOpenAI analysis: {openai_response}"
    )

    return ExecuteResponse(
        dialog_item=dialog_item,  # Passing the instance of DialogItem
        cost=TheoriqCost.zero(Currency.USDC),  # The cost can be set to zero (or calculate if needed)
        status_code=200
    )


def run_agent():
    """
    This is the main function to run the agent. It will analyze user inputs, fetch proposals,
    analyze proposals using OpenAI, and interact with the user.
    """
    try:
        logger.info("Starting DAO Voting Agent...")

        # Fetch user inputs from web3_integration
        user_inputs = get_user_inputs()
        contract_address = user_inputs['contract_address']
        abi = user_inputs['abi']
        infura_url = user_inputs['infura_url']
        wallet_address = user_inputs['wallet_address']

        # Initialize Web3 with Infura URL
        web3 = connect_to_web3(infura_url)
        if not web3.is_connected():
            logger.error("Unable to connect to Infura.")
            raise Exception("Unable to connect to Infura.")

        # Fetch wallet balance
        wallet_balance = get_wallet_balance(web3, wallet_address)

        # Fetch active proposals using proposals.py
        proposals = fetch_active_proposals()

        # Define the project's important data to analyze
        project_data = {
            'infura_url': infura_url,
            'contract_address': contract_address,
            'abi': abi,
            'wallet_address': wallet_address
        }

        # Analyze proposals and provide feedback using OpenAI before starting the conversation
        response = analyze_project_status(proposals, project_data, wallet_balance)
        logger.info(f"DAO Agent: {response}")
        print(f"DAO Agent: {response}")

        # Now, start the interactive conversation with the user
        interactive_conversation()

    except Exception as e:
        logger.error(f"Error in running the agent: {str(e)}")

        # Handle any errors and send them to OpenAI for explanation
        error_message = f"An error occurred while running the agent: {str(e)}"
        prompt = f"""
        (Remember NOT TO use bold text format for your response)
        You are an AI assistant helping with a DAO voting project. An error occurred during the process:
        {error_message}

        Can you explain this error and suggest steps to resolve it? (Remember NOT to use bold format for your response, 
        and do well to respond to users politely and don't address them as the project owner but strictly as users,
        and ensure NOT to mention that You're trained by OpenAI, just be a polite Assistant.)
        """

        # Send error response via OpenAI
        error_response = chat_with_openai_conversational(prompt)
        logger.error(f"Error response from OpenAI: {error_response}")
        print(error_response)


def run_agent_theoriq(context: ExecuteContext, request_body: ExecuteRequestBody) -> ExecuteResponse:
    """
    This function is the Theoriq-compliant version of the DAO agent runner.
    It accepts ExecuteContext and ExecuteRequestBody as parameters and returns an ExecuteResponse.
    """
    try:
        # An Example of how I'd process the Theoriq request and interact with agent.
        __ = context  # Acknowledged as parameter but not directly used here
        user_input = request_body.input  # Extract user input from request body
        logger.info(f"Processing request from Theoriq: {user_input}")

        # Simulate using OpenAI for analysis (using chat_with_openai_conversational from agent)
        openai_response = chat_with_openai_conversational(user_input)

        # Create a DialogItem for response
        dialog_item = DialogItem.new_text(
            source="DAO Voting Agent",
            text=f"Welcome to the DAO Voting Assistant.\nOpenAI analysis: {openai_response}"
        )

        # Return a valid ExecuteResponse
        return ExecuteResponse(
            dialog_item=dialog_item,
            cost=TheoriqCost.zero(Currency.USDC),
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error in running the agent: {str(e)}")

        # Handle errors and generate a friendly response
        error_message = f"An error occurred while running the agent: {str(e)}"
        return ExecuteResponse(
            dialog_item=DialogItem.new_text(
                source="DAO Voting Agent",
                text=error_message
            ),
            cost=TheoriqCost.zero(Currency.USDC),
            status_code=500
        )


if __name__ == "__main__":
    run_agent()
