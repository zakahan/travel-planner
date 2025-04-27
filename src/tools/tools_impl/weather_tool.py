import os
import asyncio
from google.adk.agents import Agent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from configs.config import tools_cfg
from mcp_servers import MCP_SERVERS_DIR
from configs import get_logger
logger = get_logger(__name__)

weather_tools_path = os.path.join(MCP_SERVERS_DIR, "weather_server.py")


async def get_weather_tools_async():
    """Gets tools from open weather MCP Server."""
    logger.debug("Attempting to connection to weather -mcp server....")

    tools, exist_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="python",
            args=[
                weather_tools_path
            ],
            env={
                "OPENWEATHER_API_KEY" : tools_cfg["mcp"]["openweathermap"]["api_key"]
            }
        )
    )
    logger.debug("Weather MCP Toolset created successfully.")

    
    return tools, exist_stack




if __name__ == "__main__":
    from agents.model import create_reasoning_model
    
    async def get_agent_async():
        tools, exit_stack = await get_weather_tools_async()
        root_agent = Agent(
            name="weather_agent",
            model=create_reasoning_model(),
            description="get weather information by using your tools.",
            instruction=(
            "The user will input location information and time, "
            "please use the tool to check the local weather."
            ),
            tools=tools
        )
        return root_agent, exit_stack

    async def async_main():
        session_service = InMemorySessionService()
        # Artifact service might not be needed for this example
        artifacts_service = InMemoryArtifactService()

        session = session_service.create_session(
            state={}, app_name='mcp_weather_app', user_id='user_01'
        )

        # TODO: Change the query to be relevant to YOUR specified folder.
        # e.g., "list files in the 'documents' subfolder" or "read the file 'notes.txt'"
        query = "帮我查询一下4月25日北京的天气"
        print(f"User Query: '{query}'")
        content = types.Content(role='user', parts=[types.Part(text=query)])

        root_agent, exit_stack = await get_agent_async()

        runner = Runner(
            app_name='mcp_weather_app',
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


    # 