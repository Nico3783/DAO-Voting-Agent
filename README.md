### DAO VOTING AGENT ###

This project implements an AI-powered DAO Voting Agent designed to interact with decentralized autonomous 
organizations (DAOs) on the Ethereum blockchain. The agent leverages OpenAI to analyze on-chain and off-chain proposals
and provides intelligent insights to users. It also integrates with Web3 to retrieve wallet balances and submit votes
on proposals.

# Features
- Wallet Integration: The agent connects to the Ethereum network and retrieves wallet balances using a Metamask wallet address.
- Proposal Fetching: Active DAO proposals are fetched either on-chain or off-chain (via the Snapshot API).
- Proposal Analysis: Utilizes OpenAI's GPT model to analyze each proposal and suggest actions.
- Automated Voting: Based on analysis and user input, the agent submits votes on the chosen DAO proposals. 
- Logging: All interactions and key processes are logged for troubleshooting and monitoring.
- User Input Management: Centralized input collection system to streamline user interactions across different components of the project.



## Project Structure ##

* Source Files (src/):
agent.py: Main agent logic.
analyze.py: OpenAI analysis on proposals.
interaction.py: User interaction logic.
main.py: Entry point for running the agent.
proposals.py: Fetches active proposals.
web3_integration.py: Handles Web3 interaction, balance retrieval, and voting.
app.py: (You may want to describe this file here).
logging_config.py: Logging functions for the project that record Agent interactions.


* Configuration Files (config/):
settings.py: Configuration settings and environment variables.
generate_key_pair.py: Key pair generation for authentication and encryption.
Other Files:

.gitignore: Specifies files and folders to ignore in version control.
.env: Environment variables (e.g., API keys, wallet address).
dao_voting_agent.log: Log file that records processes and Agent/User interactions.
README.md: Project documentation.
deploy.sh: Deployment script for publishing the agent.
requirements.txt: Python dependencies for the project.


## Setup Instructions
* Clone the repository:
  git clone https://github.com/Nico3783/DAO-Voting-Agent
  cd DAO-Voting-Agent
 
## Install dependencies: 
* Install the required Python packages listed in the requirements.txt file:
  pip install -r requirements.txt

## Configure Environment Variables: 
* Update the .env file with the following information:
- OpenAI API Key: Your OpenAI API key to analyze DAO proposals.
- Ethereum Network Details: Infura URL or other RPC provider URLs for Ethereum interaction.
- Metamask Wallet Address: Address to retrieve wallet balances and cast votes.
- Contract Address and ABI: If voting on-chain, specify the DAO contract's address and ABI.


## Generate Key Pair (Optional): 
* If needed for authentication or encryption, generate a key pair using the following script:
  python config/generate_key_pair.py





### HOW TO USE ###
**Running the Agent**
* Main Execution:* Run the main agent script to interact with the Ethereum network and analyze proposals:
  python src/main.py


## Key Functionalities:
- The agent will fetch active DAO proposals using the fetch_active_proposals() function from proposals.py.
- Proposal analysis is performed by the analyze_proposals() function in analyze.py using OpenAI.
- Based on the analysis, the agent can cast votes on the proposals, using the submit_vote() function from web3_integration.py.


## Log Output: 
  Log files will be generated for every key action taken by the agent (fetching proposals, analyzing, voting). Logs can be found under /logs for troubleshooting and verification.


## Fetching Active Proposals
  The agent fetches active proposals from two sources:
- On-chain (via Web3): Using the Ethereum network.
- Off-chain (via Snapshot API): Fetching data from the Snapshot voting system.


## Submitting a Vote
  Votes can be submitted via the submit_vote() function in web3_integration.py. This requires user confirmation before submission.


### Key Files ###
- main.py: The entry point for running the agent.
- web3_integration.py: Handles all Web3-related functions such as balance retrieval and voting.
- proposals.py: Fetches DAO proposals either from the blockchain or the Snapshot API. 
- analyze.py: Runs OpenAI's analysis on proposals and gives recommendations.


### Logging ###
Logging is implemented across the following key modules:
- proposals.py
- analyze.py
- web3_integration.py
- interaction.py
- agent.py
Logs are essential for monitoring the agent�s activities, including when proposals are fetched, analyzed, or votes are submitted. The logging configuration can be adjusted in loggin_config.py.


### Deployment ###
* To deploy the agent on Theoriq.ai, ensure that all necessary configurations (like the agent URL) are in place, and use the provided deploy.sh script:
  ./deploy.sh
* Theoriq SDK Integration: 
  The project integrates Theoriq's SDK for Web3 interaction. Ensure the SDK is correctly installed and configured by following the Theoriq installation guide.



### Known Issues ###
* Multiple User Inputs: The agent might prompt users for the same input multiple times. This is a known issue being addressed by centralizing user inputs in web3_integration.py.
* API Rate Limits: Ensure that your OpenAI API usage stays within the provided limits to avoid service interruptions.



### Future Enhancements ###
- Proposal Voting Strategy: Implementation of different voting strategies based on user preferences or historical data.
- Multi-chain Support: Extend the agent to work with multiple blockchain networks.
- Enhanced User Interface: Build a UI for easier interaction with the agent.


##### CONTACT DEVELOPER FOR MORE FOLLOW UPS #####
* Name: Nicholas Oluwakayode
For any inquiries or support, feel free to reach out to me at :
(mailto:oluwakayodenicholas1@gmail.com) or (mailto:sparkdigitals83@gmail.com).


### DAO VOTING AGENT ###