import os
from flask import Flask, request, jsonify
from theoriq import AgentConfig
from theoriq.extra.flask import theoriq_blueprint
from src.main import handle_new_proposal, handle_openai_queries, run_agent_theoriq
from src.web3_integration import connect_to_web3
from src.logging_config import setup_logger
from src.interaction import on_user_query

# Set up logging
logger = setup_logger()

logger.debug(f"Environment Variables: {os.environ}")
logger.debug(f"Current Directory Structure: {os.listdir(os.path.dirname(__file__))}")

# Initialize Flask app
app = Flask(__name__)

# Load Theoriq Agent Configuration from environment
agent_config = AgentConfig.from_env()

# Register Theoriq Blueprint with the Flask app
app.register_blueprint(theoriq_blueprint(agent_config, run_agent_theoriq))


@app.route("/")
def home():
    return jsonify({"message": "Welcome to the DAO Voting Agent API"})


@app.route("/analyze_proposal", methods=['GET', 'POST'])
def analyze_proposal():
    """
    Endpoint to handle new proposals and run analysis.
    Accepts form data containing proposal info and user details.
    """
    data = request.form
    logger.info(f"Received analyze_proposal request: {data}")

    # Extracting necessary information
    proposal = request.form.get("proposal")
    user_wallet_address = request.form.get("wallet_address")
    contract_address = request.form.get("contract_address")
    abi = request.form.get("abi")
    infura_url = request.form.get("infura_url")

    # Ensure the Ethereum Network provider URL is provided
    if not infura_url:
        logger.error("Ethereum Network provider URL is required.")
        return jsonify({"error": "Ethereum Network provider URL is required."}), 400

    web3 = connect_to_web3(infura_url)

    # Handle the proposal
    response = handle_new_proposal(proposal, web3, user_wallet_address, contract_address, abi)
    logger.info(f"analyze_proposal response: {response}")

    return jsonify({"response": response})


@app.route("/openai_query", methods=['GET', 'POST'])
def openai_query():
    """
    Endpoint for handling OpenAI conversational queries.
    """
    data = request.form
    logger.info(f"Received openai_query request: {data}")

    user_input = request.form.get("query")
    infura_url = request.form.get("infura_url")
    web3 = connect_to_web3(infura_url)
    wallet_address = request.form.get("wallet_address")
    submitted_proposals = request.form.get("submitted_proposals", [])

    # Handle the OpenAI query
    response = handle_openai_queries(user_input, web3, wallet_address, submitted_proposals)
    logger.info(f"openai_query response: {response}")

    return jsonify({"response": response})


@app.route("/user_query", methods=['GET', 'POST'])
def process_user_query():
    user_query = request.form.get("query")
    response = on_user_query(user_query)
    return jsonify({"response": response})


# Centralized error handling
@app.errorhandler(500)
def handle_internal_server_error(error):
    app.logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({"error": "Internal Server Error"}), 500


@app.errorhandler(404)
def handle_not_found(error):
    app.logger.warning(f"404 error occurred: {error}")
    return jsonify({"error": "Resource Not Found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
