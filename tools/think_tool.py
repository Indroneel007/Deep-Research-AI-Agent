from langchain_core.tools import tool

@tool
def think(summary: str) -> str:
    """
    Record a short, high-level summary of what additional
    information or reasoning is needed before proceeding.

    Use this tool when:
    - Information is missing.
    - The request is ambiguous.
    - You need to decide what question to ask next.

    Do NOT include detailed internal reasoning.
    Keep the summary brief and factual.
    """

    print(f"[THINK] {summary}")

    return f"Thought recorded: {summary}"