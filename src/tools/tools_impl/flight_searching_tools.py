import asyncio
from google.adk.agents import Agent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from tools.config import tools_cfg
from tp_logger import get_logger
logger = get_logger(__name__)


async def get_flight_tools_async():
    """Gets tools form variflight MCP Server."""
    logger.debug("Attempting to connection to variflight-mcp server....")
    # 
    tools, exist_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y",
                "@variflight-ai/variflight-mcp"
            ],
            env={
                "VARIFLIGHT_API_KEY" : tools_cfg["mcp"]["flight_mcp"]["api_key"]
            }
        )
    )
    logger.debug("MCP Toolset created successfully.")
    return tools, exist_stack


if __name__ == "__main__":
    from agents.model import create_reasoning_model
    
    async def get_agent_async():
        tools, exit_stack = await get_flight_tools_async()
        flight_agent = Agent(
            name="flight_agent",
            model=create_reasoning_model(),
            description="get flight transfer information by using your tools.",
            instruction=(
            "Given reasonable flight suggestions for the user from source location to destination."
            "Provide the flight name, departure and arrival time, price estimate, and duration in hours. "
            "Respond in plain English. Keep it concise and well-formatted."
            ),
            tools=tools
        )
        return flight_agent, exit_stack

    async def async_main():
        session_service = InMemorySessionService()
        # Artifact service might not be needed for this example
        artifacts_service = InMemoryArtifactService()

        session = session_service.create_session(
            state={}, app_name='mcp_flight_app', user_id='user_01'
        )

        # TODO: Change the query to be relevant to YOUR specified folder.
        # e.g., "list files in the 'documents' subfolder" or "read the file 'notes.txt'"
        query = "帮我选个合适的，南京到北京，2025年4月24日的航班，最好是上午的。"
        print(f"User Query: '{query}'")
        content = types.Content(role='user', parts=[types.Part(text=query)])

        root_agent, exit_stack = await get_agent_async()

        runner = Runner(
            app_name='mcp_flight_app',
            agent=root_agent,
            artifact_service=artifacts_service, # Optional
            session_service=session_service,
        )

        print("Running agent...")
        events_async = runner.run_async(
            session_id=session.id, user_id=session.user_id, new_message=content
        )

        async for event in events_async:
            print(f"Event received: {event}")

        # Crucial Cleanup: Ensure the MCP server process connection is closed.
        print("Closing MCP server connection...")
        await exit_stack.aclose()
        print("Cleanup complete.")


    asyncio.run(async_main())