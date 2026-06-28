from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv() 

llm = ChatOpenAI(
    model="openai/gpt-oss-120b:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0
)