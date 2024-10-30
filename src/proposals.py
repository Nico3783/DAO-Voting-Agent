import requests
from web3 import Web3
from src.web3_integration import get_user_inputs
from src.logging_config import setup_logger

# Set up logging
logger = setup_logger()


def find_proposal_function(abi):
    """
    Tries to find the appropriate function in the ABI to fetch proposals.
    """
    logger.info("Attempting to find proposal-related functions in ABI.")
    proposal_functions = []
    for item in abi:
        if item['type'] == 'function':
            if 'proposal' in item['name'].lower() or 'vote' in item['name'].lower():
                proposal_functions.append(item['name'])

    if proposal_functions:
        logger.info(f"Proposal-related functions found: {proposal_functions}")
        return proposal_functions
    logger.warning("No proposal-related functions found in the ABI.")
    return None


def fetch_proposals_dynamically(contract, abi):
    """
    Fetches proposals using any available proposal-related function dynamically.
    """
    proposal_functions = find_proposal_function(abi)

    if not proposal_functions:
        raise ValueError("No proposal-related function found in the ABI.")

    logger.info(f"Found proposal-related functions: {proposal_functions}")
    print(f"Found proposal-related functions: {proposal_functions}")

    for function_name in proposal_functions:
        try:
            if function_name == 'proposalCount':
                proposal_count = contract.functions.proposalCount().call()
                logger.info(f"Proposal count fetched: {proposal_count}")
                print(f"Proposal count: {proposal_count}")
                return proposal_count

            elif function_name == 'proposals':
                proposal_count = contract.functions.proposalCount().call()
                proposals = []
                for i in range(proposal_count):
                    proposal = contract.functions.proposals(i).call()
                    proposals.append(proposal)
                logger.info(f"Proposals fetched using 'proposals' function: {proposals}")
                print(f"Proposals fetched using 'proposals' function: {proposals}")
                return proposals

            elif function_name == 'getProposal':
                proposal_count = contract.functions.proposalCount().call()
                proposals = []
                for i in range(proposal_count):
                    proposal = contract.functions.getProposal(i).call()
                    proposals.append(proposal)
                logger.info(f"Proposals fetched using 'getProposal' function: {proposals}")
                print(f"Proposals fetched using 'getProposal' function: {proposals}")
                return proposals

            else:
                # In case there's a function in the ABI that does not require parameters
                result = contract.functions[function_name]().call()
                logger.info(f"Proposals fetched using {function_name} function: {result}")
                return result

        except Exception as error:
            logger.error(f"Error calling function '{function_name}': {str(error)}")
            raise error

    raise ValueError("No valid proposal function could be executed.")


def fetch_active_proposals():
    """
    Fetches active proposals either from Web3 (on-chain) or via the Snapshot API (off-chain).
    """
    # Fetch user inputs from web3_integration
    user_inputs = get_user_inputs()
    space = user_inputs['space']
    abi = user_inputs['abi']
    contract_address = user_inputs['contract_address']
    infura_url = user_inputs['infura_url']

    # Log user inputs
    logger.info(f"Fetching active proposals for "
                f"space: {space}, contract: {contract_address}, Infura URL: {infura_url}")

    # Printing user inputs for clarity
    print("\n--- Fetching Active Proposals ---")
    print(f"DAO Space: {space}")
    if abi:
        print("ABI Provided: Yes")
    else:
        print("ABI Provided: No")

    if contract_address:
        print(f"Contract Address: {contract_address}")
    else:
        print("Contract Address: None Provided")

    if infura_url:
        print(f"Infura URL: {infura_url}")
    else:
        print("Infura URL: None Provided")

    # Fetch on-chain proposals if all parameters are provided
    if abi and contract_address and infura_url:
        logger.info("Attempting to fetch on-chain proposals...")
        print("\nAttempting to fetch on-chain proposals...")
        try:
            web3 = Web3(Web3.HTTPProvider(infura_url))
            if not web3.is_connected():
                raise Exception("Unable to connect to Infura.")

            contract = web3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
            onchain_proposals = fetch_proposals_dynamically(contract, abi)

            if onchain_proposals:
                logger.info(f"On-chain proposals fetched successfully: {onchain_proposals}")
                print("\nOn-chain proposals fetched successfully.")
                return onchain_proposals
            else:
                logger.warning("No on-chain proposals found or an error occurred.")
                print("\nNo on-chain proposals found or an error occurred.")
        except Exception as error:
            logger.error(f"Error while fetching on-chain proposals: {str(error)}")
            print(f"Error while fetching on-chain proposals: {str(error)}")

    # Fallback to fetching off-chain proposals via Snapshot API
    logger.info("Fetching off-chain proposals via Snapshot API...")
    print("\nFetching off-chain proposals via Snapshot API...")
    url = "https://hub.snapshot.org/graphql"
    query = f"""
    {{
      proposals(first: 5, where: {{ space_in: ["{space}"], state: "active" }}) {{
        id
        title
        body
        choices
        start
        end
      }}
    }}
    """
    response = requests.post(url, json={'query': query})

    if response.status_code == 200:
        data = response.json()
        offchain_proposals = data['data']['proposals']
        if offchain_proposals:
            logger.info(f"Off-chain proposals fetched successfully: {offchain_proposals}")
            print(f"\n{len(offchain_proposals)} off-chain proposals found.")
            return offchain_proposals
        else:
            logger.warning("No active off-chain proposals found.")
            print("\nNo active off-chain proposals found.")
            return []
    else:
        logger.error(f"Error fetching proposals from Snapshot API: {response.status_code}")
        print(f"\nError fetching proposals from Snapshot API: {response.status_code}")
        return []


# A short example function call to test the implementation
if __name__ == "__main__":
    try:
        proposals_data = fetch_active_proposals()
        logger.info(f"Proposals fetched: {proposals_data}")
        print("\nProposals Fetched:")
        print(proposals_data)
    except Exception as e:
        logger.error(f"Error in fetching proposals: {str(e)}")
        print(f"Error in fetching proposals: {str(e)}")
        print(f"Error: {str(e)}")
