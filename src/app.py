from flask import Flask, request, jsonify
from theoriq import AgentConfig
from theoriq.extra.flask import theoriq_blueprint
from main import handle_new_proposal, handle_openai_queries, run_agent_theoriq
from web3_integration import connect_to_web3
import os
from logging_config import setup_logger

# Set up logging
logger = setup_logger()

# Initialize Flask app
app = Flask(__name__)

# Loading agent configuration from environment variables
agent_config = AgentConfig.from_env()

# Theoriq blueprint Registration (pass function reference, not invocation)
app.register_blueprint(theoriq_blueprint(agent_config, run_agent_theoriq))


# Add a home route to avoid 404 errors
@app.route("/")
def home():
    """
    Home route to give information about the API.
    """
    return jsonify({"message": "DAO Voting Agent API. Use the appropriate endpoints "
                               "like /analyze_proposal or /openai_query."})


# Define additional custom endpoints
@app.route("/analyze_proposal", methods=["POST"])
def analyze_proposal():
    """
    Endpoint to handle new proposals and run analysis.
    Accepts JSON data containing proposal info and user details.
    """
    data = request.get_json()

    # Log the received data
    logger.info(f"Received analyze_proposal request: {data}")

    # Extracting necessary information
    proposal = data.get("proposal")
    user_wallet_address = data.get("wallet_address")
    contract_address = data.get("contract_address")
    abi = data.get("abi")

    # Handling the proposal
    infura_url = data.get("infura_url")
    web3 = connect_to_web3(infura_url)

    response = handle_new_proposal(proposal, web3, user_wallet_address, contract_address, abi)

    # Log the response
    logger.info(f"analyze_proposal response: {response}")

    return jsonify({"response": response})


@app.route("/openai_query", methods=["POST"])
def openai_query():
    """
    Endpoint for handling OpenAI conversational queries.
    """
    data = request.get_json()

    # Log the received data
    logger.info(f"Received openai_query request: {data}")

    user_input = data.get("query")
    infura_url = data.get("infura_url")
    web3 = connect_to_web3(infura_url)
    wallet_address = data.get("wallet_address")
    submitted_proposals = data.get("submitted_proposals", [])

    # Handle the OpenAI query
    response = handle_openai_queries(user_input, web3, wallet_address, submitted_proposals)

    # Log the response
    logger.info(f"openai_query response: {response}")

    return jsonify({"response": response})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    # Log app start
    logger.info("Starting Flask app on port %s", port)

    app.run(host="0.0.0.0", port=port)
