# LangVoice SDK - AI Framework Integration Examples

This directory contains examples for integrating LangVoice with popular AI agent frameworks.

## 🎯 Quick Start

Set your API keys once at the top of each example file, and you're ready to go!

---

## 📦 Supported Frameworks

| Framework | Example File | Toolkit Class |
|-----------|--------------|---------------|
| **OpenAI** | `example_openai.py` | `LangVoiceOpenAITools` |
| **LangChain** | `example_langchain.py` | `LangVoiceLangChainToolkit` |
| **AutoGen** | `example_autogen.py` | `LangVoiceAutoGenToolkit` |
| **CrewAI** | `example_crewai.py` | `LangVoiceCrewAIToolkit` |
| **Generic** | `example_generic.py` | `LangVoiceToolkit` |

---

## 🔧 OpenAI Integration

```python
from openai import OpenAI
from langvoice.tools import LangVoiceOpenAITools

# Set API keys once
openai_client = OpenAI(api_key="your-openai-key")
langvoice = LangVoiceOpenAITools(api_key="your-langvoice-key")

# Make request with all tools
response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Generate speech saying hello"}],
    tools=langvoice.get_tools()
)

# Handle tool calls - NO API key needed each time!
for tool_call in response.choices[0].message.tool_calls:
    result = langvoice.handle_call(tool_call)
    langvoice.save_audio_from_result(result, "output.mp3")
```

---

## 🦜 LangChain Integration

```python
from langchain_openai import ChatOpenAI
from langvoice.tools.langchain_tools import LangVoiceLangChainToolkit

# Initialize toolkit
toolkit = LangVoiceLangChainToolkit(api_key="your-langvoice-key")

# Get all tools for your agent
tools = toolkit.get_tools()

# Use with LangChain agents
llm = ChatOpenAI(model="gpt-4o")
agent = create_openai_tools_agent(llm, tools, prompt)
```

---

## 🤖 AutoGen Integration

```python
from autogen import AssistantAgent, UserProxyAgent
from langvoice.tools.autogen_tools import LangVoiceAutoGenToolkit

# Initialize toolkit
toolkit = LangVoiceAutoGenToolkit(api_key="your-langvoice-key")

# Get function schemas for LLM config
llm_config = {
    "functions": toolkit.get_function_schemas(),
}

# Register functions with user proxy
for func in toolkit.get_functions():
    user_proxy.register_function(function_map={func.__name__: func})
```

---

## 👥 CrewAI Integration

```python
from crewai import Agent, Crew
from langvoice.tools.crewai_tools import LangVoiceCrewAIToolkit

# Initialize toolkit
toolkit = LangVoiceCrewAIToolkit(api_key="your-langvoice-key")

# Create agent with LangVoice tools
agent = Agent(
    role="Voice Generator",
    goal="Generate natural speech",
    tools=toolkit.get_tools()
)
```

---

## 🔌 Generic/Universal Integration

Works with ANY framework: LlamaIndex, Semantic Kernel, Haystack, custom frameworks, etc.

```python
from langvoice.tools import LangVoiceToolkit

# Initialize toolkit
toolkit = LangVoiceToolkit(api_key="your-langvoice-key")

# Direct usage
result = toolkit.text_to_speech("Hello world!", voice="heart")
toolkit.save_audio(result, "output.mp3")

# Handle tool calls from any LLM
result = toolkit.handle_tool_call("langvoice_text_to_speech", {"text": "Hello"})

# Get schemas for any framework
schemas = toolkit.get_function_schemas()
```

---

## 🛠️ Available Tools

All frameworks provide these 4 tools:

| Tool | Description |
|------|-------------|
| `langvoice_text_to_speech` | Convert text to speech |
| `langvoice_multi_voice_speech` | Generate speech with multiple voices |
| `langvoice_list_voices` | Get available voices |
| `langvoice_list_languages` | Get supported languages |

---

## 📋 Installation

```bash
# Base SDK
pip install langvoice

# With LangChain support
pip install langvoice[langchain]

# With all optional dependencies
pip install langvoice openai langchain crewai pyautogen
```

---

## 🎤 Available Voices

### American Voices
`heart`, `bella`, `nicole`, `sarah`, `nova`, `sky`, `jessica`, `river`, `michael`, `fenrir`, `eric`, `liam`, `onyx`, `adam`

### British Voices
`emma`, `isabella`, `alice`, `lily`, `george`, `fable`, `lewis`, `daniel`

---

## 🌍 Supported Languages

- `american_english`
- `british_english`
- `spanish`
- `french`
- `hindi`
- `italian`
- `japanese`
- `brazilian_portuguese`
- `mandarin_chinese`

---

## 📧 Support

For questions or issues, visit: https://www.langvoice.pro
