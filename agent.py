from langgraph import StateGraph
from langgraph.prebuilt import ToolNode
from 
from typing import TypedDict
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

# Define the state schema (e.g., messages, memory)
class AgentState(TypedDict):
    messages: list[BaseMessage]

# Build the workflow graph
workflow = StateGraph(AgentState)
# Node that calls the LLM on current messages
async def call_llm(state: AgentState):
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}
# Add nodes and edges
workflow.add_node("llm", call_llm)
workflow.add_node("tools", ToolNode(list_of_tools))
workflow.add_edge("tools", "llm")
workflow.add_edge("llm", "tools")
compiled_agent = workflow.compile()

# To run the agent:
initial_state = {"messages": [HumanMessage(content=user_query)]}
result = await compiled_agent.ainvoke(initial_state)
final_answer = result["messages"][-1].content