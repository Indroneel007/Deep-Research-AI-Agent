from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langgraph.graph import END
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from tools.think_tool import think
from prompts import RESEARCH_BRIEF_PROMPT
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

    # Produced by the Research Brief Agent
    research_brief: Optional[str]

    # Optional: supervisor decision
    next_agent: Optional[str]

# Build the workflow graph
workflow = StateGraph(AgentState)
# Node that calls the LLM on current messages
async def call_llm(state: AgentState):
    forced_llm = llm.bind_tools(
        list_of_tools,
        tool_choice="think"
    )

    response = await forced_llm.ainvoke(state["messages"])
    return {"messages": [response]}

async def research_brief_node(state: AgentState):

    messages = [
        SystemMessage(content=RESEARCH_BRIEF_PROMPT)
    ] + state["messages"]

    response = await llm.ainvoke(messages)

    return {
        "research_brief": response.content
    }

workflow = StateGraph(AgentState)

workflow.add_node("clarify_agent", call_llm)
workflow.add_node("tools", ToolNode(list_of_tools))
workflow.add_node("research_brief", research_brief_node)

workflow.set_entry_point("clarify_agent")

workflow.add_conditional_edges(
    "clarify_agent",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)

workflow.add_edge("tools", "clarify_agent")
workflow.add_edge("clarify_agent","research_brief")

graph = workflow.compile()

async def main():
    result = await graph.ainvoke(
        {
            "messages": [
                HumanMessage(content="Explain me meaning of biodiversity")
            ]
        }
    )

    print("\n=== Clarify Agent Output ===")
    print(result["messages"][-1].content)

    print("\n=== Research Brief ===")
    print(result.get("research_brief", "No research brief generated"))


if __name__ == "__main__":
    asyncio.run(main())