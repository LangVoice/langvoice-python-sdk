"""
LangVoice SDK - LangChain Integration Example
==============================================

This example shows how to use LangVoice with LangChain agents.

Requirements:
    pip install langchain langchain-openai langvoice
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langvoice.tools.langchain_tools import LangVoiceLangChainToolkit

# ============================================
# CONFIGURATION - Set your API keys once
# ============================================
OPENAI_API_KEY = "your-openai-api-key"
LANGVOICE_API_KEY = "your-langvoice-api-key"

# Initialize LangVoice toolkit
toolkit = LangVoiceLangChainToolkit(api_key=LANGVOICE_API_KEY)


def main():
    # ============================================
    # CREATE LANGCHAIN AGENT WITH LANGVOICE TOOLS
    # ============================================
    
    # Get all LangVoice tools
    tools = toolkit.get_tools()
    print(f"Available tools: {[t.name for t in tools]}")
    
    # Create LLM
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=OPENAI_API_KEY,
    )
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant with text-to-speech capabilities."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # ============================================
    # RUN AGENT
    # ============================================
    result = agent_executor.invoke({
        "input": "Generate speech saying 'Hello from LangChain!' and tell me about available voices."
    })
    
    print(f"\n📊 Result: {result['output']}")


if __name__ == "__main__":
    main()
