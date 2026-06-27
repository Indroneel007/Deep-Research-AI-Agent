from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from typing import TypedDict, Annotated
from openai import AsyncOpenAI
from langgraph.graph.message import add_messages
from langgraph.graph import END
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from tools.think_tool import think
import asyncio
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

load_dotenv()  # Load environment variables from .env file

llm = ChatOpenAI(
    model="openai/gpt-oss-120b:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0
)

list_of_tools = [think]

# Define the state schema (e.g., messages, memory)
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Bind tools with llm
llm_with_tools = llm.bind_tools(list_of_tools)

# Build the workflow graph
workflow = StateGraph(AgentState)
# Node that calls the LLM on current messages
async def call_llm(state: AgentState):
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}


workflow = StateGraph(AgentState)

workflow.add_node("llm", call_llm)
workflow.add_node("tools", ToolNode(list_of_tools))

workflow.set_entry_point("llm")

workflow.add_conditional_edges(
    "llm",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)

workflow.add_edge("tools", "llm")

graph = workflow.compile()

async def main():
    result = await graph.ainvoke(
        {
            "messages": [
                HumanMessage(content="What is 45 + 21?")
            ]
        }
    )

    print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())