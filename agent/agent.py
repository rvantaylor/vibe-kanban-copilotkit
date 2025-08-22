"""
This is the main entry point for the agent.
It defines the workflow graph, state, tools, nodes and edges.
"""

import os
from crewai import Task
from numpy import number
from typing_extensions import Literal
from typing import TypedDict
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langgraph.prebuilt import ToolNode
from copilotkit import CopilotKitState

class AgentState(CopilotKitState):
    pass

    # your_custom_agent_state: str = ""

@tool
def get_weather(location: str):
    """
    Get the weather for a given location.
    """
    return f"The weather for {location} is 70 degrees."

tools = [
    get_weather
]

async def chat_node(state: AgentState, config: RunnableConfig) -> Command[Literal["tool_node", "__end__"]]:
    """
    Standard chat node based on the ReAct design pattern. It handles:
    - The model to use (and binds in CopilotKit actions and the tools defined above)
    - The system prompt
    - Getting a response from the model
    - Handling tool calls

    For more about the ReAct design pattern, see:
    https://www.perplexity.ai/search/react-agents-NcXLQhreS0WDzpVaS4m9Cg
    """

    # 1. Define the model
    from langchain_anthropic import ChatAnthropic
    from dotenv import load_dotenv
    load_dotenv()
    model = ChatAnthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model_name=os.getenv("MODEL_NAME"),
        base_url=os.getenv("BASE_URL")
    )
    
    # 2. Bind the tools to the model
    model_with_tools = model.bind_tools(
        [
            *state["copilotkit"]["actions"],
            get_weather,
        ],
    )

    # 3. Define the system message by which the chat model will be run
    system_message = SystemMessage(
        content="""You are a helpful assistant."""
    )

    # 4. Run the model to generate a response
    response = await model_with_tools.ainvoke([
        system_message,
        *state["messages"],
    ], config)

    # 5. Check for tool calls in the response and handle them. We ignore
    #    CopilotKit actions, as they are handled by CopilotKit.
    if isinstance(response, AIMessage) and response.tool_calls:
        actions = state["copilotkit"]["actions"]

        # 5.1 Check for any non-copilotkit actions in the response and
        #     if there are none, go to the tool node.
        if not any(
            action.get("name") == response.tool_calls[0].get("name")
            for action in actions
        ):
            return Command(goto="tool_node", update={"messages": response})

    # 6. We've handled all tool calls, so we can end the graph.
    return Command(
        goto=END,
        update={
            "messages": response
        }
    )

# Define the workflow graph
workflow = StateGraph(AgentState)
workflow.add_node("chat_node", chat_node)
workflow.add_node("tool_node", ToolNode(tools=tools))
workflow.add_edge("tool_node", "chat_node")
workflow.set_entry_point("chat_node")


# For CopilotKit and other contexts, use MemorySaver
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

async def main():
    """Test the agent locally"""
    from langchain_core.messages import HumanMessage
    
    test_state = AgentState(
        messages=[HumanMessage(content="Hello! What's the weather like in San Francisco?")],
        copilotkit={"actions": []}
    )
    config = RunnableConfig(configurable={"thread_id": "test"})
    
    print("🧪 Testing agent locally...")
    result = await graph.ainvoke(test_state, config)
    print(f"✅ Agent response: {result['messages'][-1].content}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
