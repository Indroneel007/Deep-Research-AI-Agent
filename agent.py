from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langgraph.graph import END
from dotenv import load_dotenv
from config.llm import llm
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

list_of_tools = [think]

# Define the state schema (e.g., messages, memory)
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

    research_brief: Optional[str]

    needs_clarification: Optional[bool]
    clarification_questions: Optional[list[str]]
    clarification_answers: Optional[dict[str, str]]

# Build the workflow graph
workflow = StateGraph(AgentState)
# Node that calls the LLM on current messages
from langchain_core.messages import AIMessage


async def call_llm(state: AgentState):

    forced_llm = llm.bind_tools(
        list_of_tools,
        tool_choice="think"
    )

    response = await forced_llm.ainvoke(state["messages"])

    # Default values
    results = {
        "messages": [response],
        "needs_clarification": False,
        "clarification_questions": []
    }

    # Check if the model called the tool
    if response.tool_calls:
        tool_call = response.tool_calls[0]

        # Assuming the tool returns:
        # {
        #   "needs_clarification": bool,
        #   "questions": [...]
        # }

        tool_result = await think.ainvoke(tool_call["args"])

        results["needs_clarification"] = tool_result[
            "needs_clarification"
        ]

        results["clarification_questions"] = tool_result[
            "questions"
        ]

    return results

def clarification_router(state: AgentState):

    if state["needs_clarification"]:
        return END

    return "research_brief"
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
workflow.add_node("research_brief", research_brief_node)

workflow.set_entry_point("clarify_agent")

workflow.add_conditional_edges(
    "clarify_agent",
    clarification_router,
    {
        "research_brief": "research_brief",
        END: END
    }
)

workflow.add_edge("research_brief", END)

graph = workflow.compile()

async def main():

    state = {
        "messages": [
            HumanMessage(
                content=input("User: ")
            )
        ],
        "clarification_answers": {}
    }

    while True:

        result = await graph.ainvoke(state)

        if result.get("needs_clarification"):

            question = result["clarification_questions"][0]

            print(f"\nAssistant: {question}")

            answer = input("You: ")

            answers = result.get(
                "clarification_answers", {}
            )

            answers[question] = answer

            state = {
                **result,
                "clarification_answers": answers,
                "messages": result["messages"] + [
                    HumanMessage(
                        content=f"{question}\nAnswer: {answer}"
                    )
                ]
            }

            continue

        print("\n=== Final Research Brief ===")
        print(result["research_brief"])
        break


if __name__ == "__main__":
    asyncio.run(main())