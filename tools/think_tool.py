from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from config.llm import llm   # wherever your llm object lives


class ClarificationOutput(BaseModel):
    needs_clarification: bool
    questions: list[str]


@tool(
    description="Analyze a user query and generate clarification questions if required."
)
async def think(query: str) -> dict:    
    """
    Analyze a query and determine whether clarification is needed.
    """

    CLARIFY_AGENT_PROMPT = """
    You are a Clarification Agent.

    Your job is to determine whether the user's request contains enough information
    to complete the task.

    If enough information is present return:

    {
        "needs_clarification": false,
        "questions": []
    }

    Otherwise ask at most 3 questions.
    """

    structured_llm = llm.with_structured_output(
        ClarificationOutput
    )

    result = await structured_llm.ainvoke([
        SystemMessage(content=CLARIFY_AGENT_PROMPT),
        HumanMessage(content=query)
    ])

    return {
        "needs_clarification": result.needs_clarification,
        "questions": result.questions
    }