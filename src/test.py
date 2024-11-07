def run_agent():
    """Main agent function to initialize, fetch proposals, analyze status, and interact with the user."""
    try:
        logger.info("Starting DAO Voting Agent...")
        logger.info(f"Received request: {context.request_id}")

        # Gather user and web3 configuration inputs
        user_inputs = get_user_inputs()
        contract_address, abi, infura_url, wallet_address = (user_inputs['contract_address'],
                                                             user_inputs['abi'],
                                                             user_inputs['infura_url'],
                                                             user_inputs['wallet_address'])

        # Process the last text block from the request body as user input
        last_block = request_body.last_item.blocks[0]
        user_input = last_block.data.text
        logger.info(f"Processing user input: {user_input}")


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

        return context.new_response(
            blocks=[TextItemBlock(text=response)],
            cost=TheoriqCost(amount=1, currency=Currency.USDC)
        )

        # Start interactive conversation
        interactive_conversation()

    except Exception as e:
        logger.error(f"Error in running the agent: {str(e)}")
        handle_agent_error(e)



def run_agent_theoriq(context: ExecuteContext, request_body: ExecuteRequestBody) -> ExecuteResponse:
    """Theoriq-compliant agent execution function that calls the DAO Voting Agent."""
    try:
        logger.info(f"Received request: {context.request_id}")

        # Process the last text block from the request body as user input
        last_block = request_body.last_item.blocks[0]
        user_input = last_block.data.text
        logger.info(f"Processing user input: {user_input}")

        # Run the DAO Voting Agent logic
        try:
            # Call run_agent() to perform the main agent tasks
            run_agent()

            # Assume run_agent logs results and displays output. Here, we capture a general success message.
            response_text = "DAO Voting Agent ran successfully, and proposals were analyzed."
        except Exception as inner_e:
            response_text = f"An error occurred while running the DAO Voting Agent: {str(inner_e)}"
            logger.error(response_text)

        # Build a Theoriq-compatible response
        return context.new_response(
            blocks=[TextItemBlock(text=response_text)],
            cost=TheoriqCost(amount=1, currency=Currency.USDC)
        )

    except Exception as e:
        # Catch any outer exceptions and handle them as an error response
        logger.error(f"Error in run_agent_theoriq: {str(e)}")
        return context.new_response(
            blocks=[TextItemBlock(text=f"An unexpected error occurred: {str(e)}")],
            cost=TheoriqCost.zero(Currency.USDC)
        )