
<h1 align="center">🎤 LangVoice Python SDK</h1>

<p align="center">
  <img src="https://i.ibb.co/svWyWcR6/logo.png" alt="LangVoice Logo" width="400"/>
</p>


<p align="center">
  <a href="https://badge.fury.io/py/langvoice"><img src="https://badge.fury.io/py/langvoice.svg" alt="PyPI version"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

<p align="center">
  The official Python SDK for <a href="https://www.langvoice.pro/">LangVoice</a> - Professional Text-to-Speech API with natural-sounding voices, multi-language support, and seamless AI agent integration.
</p>

---

## ✨ Features

- 🗣️ **28+ Natural Voices** - Male and female voices with unique personalities
- 🌍 **9 Languages** - American English, British English, Spanish, French, Hindi, Italian, Japanese, Portuguese, Chinese
- 🎭 **Multi-Voice Synthesis** - Multiple voices in a single audio using bracket notation
- ⚡ **Async Support** - Full async/await support for high-performance applications
- 🤖 **AI Agent Integration** - Ready-to-use tools for OpenAI, LangChain, AutoGen, CrewAI, and more
- 📦 **Simple API** - Clean, intuitive interface with comprehensive documentation

---

## 📦 Installation

```bash
pip install langvoice
```

With optional dependencies:
```bash
# For LangChain integration
pip install langvoice[langchain]

# For all AI frameworks
pip install langvoice openai langchain crewai pyautogen
```

---

## 🚀 Quick Start

### Get Your API Key

1. Visit [https://www.langvoice.pro/](https://www.langvoice.pro/)
2. Sign up and get your API key
3. Set it as an environment variable or pass it directly

```bash
export LANGVOICE_API_KEY="your-api-key"
```

---

## 📖 Basic Usage

### Generate Speech

```python
from langvoice import LangVoiceClient

# Initialize client
client = LangVoiceClient(api_key="your-api-key")
# Or set LANGVOICE_API_KEY environment variable

# Generate speech
response = client.generate(
    text="Hello, world! Welcome to LangVoice.",
    voice="heart",
    language="american_english",
    speed=1.0
)

# Save to file
with open("output.mp3", "wb") as f:
    f.write(response.audio_data)

print(f"Duration: {response.duration}s")
print(f"Characters: {response.characters_processed}")
```

### Multi-Voice Generation

Create conversations or podcasts with multiple voices:

```python
from langvoice import LangVoiceClient

client = LangVoiceClient(api_key="your-api-key")

# Use [voice_name] to switch voices
response = client.generate_multi_voice(
    text="[heart] Welcome to our podcast! [michael] Thanks for having me! [heart] Let's get started.",
    language="american_english"
)

with open("podcast.mp3", "wb") as f:
    f.write(response.audio_data)
```

### List Available Voices

```python
from langvoice import LangVoiceClient

client = LangVoiceClient(api_key="your-api-key")

voices = client.list_voices()
for voice in voices:
    print(f"{voice.id}: {voice.name} ({voice.gender})")
```

**Output:**
```
heart: Heart (female)
bella: Bella (female)
michael: Michael (male)
...
```

### List Supported Languages

```python
from langvoice import LangVoiceClient

client = LangVoiceClient(api_key="your-api-key")

languages = client.list_languages()
for lang in languages:
    print(f"{lang.id}: {lang.name}")
```

**Output:**
```
american_english: American English
british_english: British English
spanish: Spanish
french: French
hindi: Hindi
italian: Italian
japanese: Japanese
brazilian_portuguese: Brazilian Portuguese
mandarin_chinese: Mandarin Chinese
```

---

## ⚡ Async Usage

For high-performance applications, use the async client:

### Async Speech Generation

```python
import asyncio
from langvoice.async_client import AsyncLangVoiceClient

async def main():
    async with AsyncLangVoiceClient(api_key="your-api-key") as client:
        response = await client.generate(
            text="Hello from async LangVoice!",
            voice="heart"
        )
        
        print(f"Generated audio: {len(response.audio_data)} bytes")
        print(f"Duration: {response.duration}s")
        
        with open("output.mp3", "wb") as f:
            f.write(response.audio_data)

if __name__ == "__main__":
    asyncio.run(main())
```

### Async Multi-Voice

```python
import asyncio
from langvoice.async_client import AsyncLangVoiceClient

async def main():
    async with AsyncLangVoiceClient(api_key="your-api-key") as client:
        response = await client.generate_multi_voice(
            text="[heart] Hello! [michael] How are you?"
        )
        
        with open("conversation.mp3", "wb") as f:
            f.write(response.audio_data)
        print(f"Duration: {response.duration}s")

if __name__ == "__main__":
    asyncio.run(main())
```

### Async List Voices & Languages

```python
import asyncio
from langvoice.async_client import AsyncLangVoiceClient

async def main():
    async with AsyncLangVoiceClient(api_key="your-api-key") as client:
        # List voices
        voices = await client.list_voices()
        print(f"Available voices: {len(voices)}")
        
        # List languages
        languages = await client.list_languages()
        print(f"Supported languages: {len(languages)}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🤖 AI Agent Integration

LangVoice integrates seamlessly with popular AI agent frameworks.

### OpenAI Function Calling

```python
from openai import OpenAI
from langvoice.tools import LangVoiceOpenAITools

# Set API keys once
openai_client = OpenAI(api_key="your-openai-key")
langvoice = LangVoiceOpenAITools(api_key="your-langvoice-key")

# Make request with LangVoice tools
response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Generate speech saying: Hello World!"}],
    tools=langvoice.get_tools()  # 4 tools available
)

print(f"Tools available: {len(langvoice.get_tools())}")

# Handle tool calls - NO API key needed each time!
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"🔧 {tool_call.function.name}")
        
        result = langvoice.handle_call(tool_call)
        
        print(f"   Success: {result.get('success')}")
        print(f"   Duration: {result.get('duration')}s")
        
        # Save audio
        if langvoice.save_audio_from_result(result, "output.mp3"):
            print("   ✅ Saved to output.mp3")
```

### LangChain Integration

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langvoice.tools.langchain_tools import LangVoiceLangChainToolkit

# Initialize toolkit - API key set once
toolkit = LangVoiceLangChainToolkit(api_key="your-langvoice-key")

# Get all tools (TTS auto-saves to output.mp3)
tools = toolkit.get_tools()
print(f"Available tools: {[t.name for t in tools]}")

# Create LLM and agent
llm = ChatOpenAI(model="gpt-4o", api_key="your-openai-key")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with text-to-speech capabilities."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run agent
result = agent_executor.invoke({
    "input": "Generate speech saying 'Hello from LangChain!'"
})

print(f"Result: {result['output']}")
# Audio automatically saved to output.mp3
```

### AutoGen Integration

```python
from autogen import AssistantAgent, UserProxyAgent
from langvoice.tools.autogen_tools import LangVoiceAutoGenToolkit

# Initialize toolkit
toolkit = LangVoiceAutoGenToolkit(api_key="your-langvoice-key")

# Get function schemas
llm_config = {
    "config_list": [{"model": "gpt-4o", "api_key": "your-openai-key"}],
    "functions": toolkit.get_function_schemas(),
}

# Create agents
assistant = AssistantAgent(
    name="voice_assistant",
    system_message="You can generate speech using LangVoice.",
    llm_config=llm_config,
)

user_proxy = UserProxyAgent(name="user_proxy", human_input_mode="NEVER")

# Register functions
for func in toolkit.get_functions():
    user_proxy.register_function(function_map={func.__name__: func})

# Simple usage
result = toolkit.text_to_speech("Hello from AutoGen!", voice="heart")
toolkit.save_audio_from_result(result, "output.mp3")
```

### CrewAI Integration

```python
from crewai import Agent, Task, Crew
from langvoice.tools.crewai_tools import LangVoiceCrewAIToolkit

# Initialize toolkit
toolkit = LangVoiceCrewAIToolkit(api_key="your-langvoice-key")

# Create agent with LangVoice tools
voice_agent = Agent(
    role="Voice Generator",
    goal="Generate natural-sounding speech",
    backstory="You are an expert at creating voice content.",
    tools=toolkit.get_tools(),  # TTS auto-saves to output.mp3
    verbose=True,
)

# Create task
voice_task = Task(
    description="Generate speech saying 'Hello from CrewAI!'",
    expected_output="Confirmation with duration",
    agent=voice_agent,
)

# Run crew
crew = Crew(agents=[voice_agent], tasks=[voice_task])
result = crew.kickoff()
```

### Generic/Universal Toolkit

Works with ANY AI framework (LlamaIndex, Semantic Kernel, Haystack, custom frameworks):

```python
from langvoice.tools import LangVoiceToolkit

# Initialize toolkit
toolkit = LangVoiceToolkit(api_key="your-langvoice-key")

# Direct usage
result = toolkit.text_to_speech(
    text="Hello from LangVoice!",
    voice="heart",
    language="american_english"
)
toolkit.save_audio(result, "output.mp3")
print(f"Duration: {result['duration']}s")

# Multi-voice
result = toolkit.multi_voice_speech(
    text="[heart] Hello! [michael] Hi there!"
)
toolkit.save_audio(result, "conversation.mp3")

# List resources
voices = toolkit.list_voices()
languages = toolkit.list_languages()

# Handle tool calls from any LLM
result = toolkit.handle_tool_call(
    "langvoice_text_to_speech",
    {"text": "Hello!", "voice": "nova"}
)

# Get OpenAI-compatible schemas for any framework
schemas = toolkit.get_function_schemas()
openai_tools = toolkit.get_openai_tools()
```

---

## 🎤 Available Voices

### Female Voices
| ID | Name | Accent |
|----|------|--------|
| heart | Heart | American |
| bella | Bella | American |
| nicole | Nicole | American |
| sarah | Sarah | American |
| nova | Nova | American |
| sky | Sky | American |
| jessica | Jessica | American |
| river | River | American |
| aoede | Aoede | American |
| kore | Kore | American |
| alloy | Alloy | American |
| emma | Emma | British |
| isabella | Isabella | British |
| alice | Alice | British |
| lily | Lily | British |

### Male Voices
| ID | Name | Accent |
|----|------|--------|
| michael | Michael | American |
| fenrir | Fenrir | American |
| eric | Eric | American |
| liam | Liam | American |
| onyx | Onyx | American |
| adam | Adam | American |
| puck | Puck | American |
| echo | Echo | American |
| santa | Santa | American |
| george | George | British |
| fable | Fable | British |
| lewis | Lewis | British |
| daniel | Daniel | British |

---

## 🌍 Supported Languages

| ID | Name |
|----|------|
| american_english | American English |
| british_english | British English |
| spanish | Spanish |
| french | French |
| hindi | Hindi |
| italian | Italian |
| japanese | Japanese |
| brazilian_portuguese | Brazilian Portuguese |
| mandarin_chinese | Mandarin Chinese |

---

## 🔧 API Reference

### LangVoiceClient

```python
client = LangVoiceClient(
    api_key="your-key",     # Or use LANGVOICE_API_KEY env var
    base_url=None,          # Custom API URL (optional)
    timeout=60              # Request timeout in seconds
)
```

### Methods

| Method | Description |
|--------|-------------|
| `generate(text, voice, language, speed)` | Generate speech from text |
| `generate_multi_voice(text, language, speed)` | Multi-voice generation |
| `list_voices()` | Get available voices |
| `list_languages()` | Get supported languages |
| `text_to_speech(text, voice, language, speed)` | Simple TTS (returns bytes) |

### GenerateResponse

```python
response.audio_data          # bytes - MP3 audio data
response.duration            # float - Duration in seconds
response.generation_time     # float - Generation time
response.characters_processed # int - Characters processed
```

---

## 🛠️ AI Tools Reference

### Available Tools

All AI integrations provide these 4 tools:

| Tool Name | Description |
|-----------|-------------|
| `langvoice_text_to_speech` | Convert text to speech |
| `langvoice_multi_voice_speech` | Multi-voice generation |
| `langvoice_list_voices` | List available voices |
| `langvoice_list_languages` | List supported languages |

### Toolkit Classes

| Framework | Class | Import |
|-----------|-------|--------|
| OpenAI | `LangVoiceOpenAITools` | `from langvoice.tools import LangVoiceOpenAITools` |
| LangChain | `LangVoiceLangChainToolkit` | `from langvoice.tools.langchain_tools import LangVoiceLangChainToolkit` |
| AutoGen | `LangVoiceAutoGenToolkit` | `from langvoice.tools.autogen_tools import LangVoiceAutoGenToolkit` |
| CrewAI | `LangVoiceCrewAIToolkit` | `from langvoice.tools.crewai_tools import LangVoiceCrewAIToolkit` |
| Generic | `LangVoiceToolkit` | `from langvoice.tools import LangVoiceToolkit` |

---

## 📁 Examples

Check the `examples/` directory for complete working examples:

- `example_openai.py` - OpenAI function calling
- `example_langchain.py` - LangChain agent integration
- `example_autogen.py` - Microsoft AutoGen integration
- `example_crewai.py` - CrewAI integration
- `example_generic.py` - Universal/generic usage

---

## 🔗 Links

- **Website**: [https://www.langvoice.pro/](https://www.langvoice.pro/)
- **Get API Key**: [https://www.langvoice.pro/](https://www.langvoice.pro/)
- **GitHub**: [https://github.com/LangVoice](https://github.com/LangVoice)
- **LinkedIn**: [https://www.linkedin.com/company/langvoice](https://www.linkedin.com/company/langvoice)
- **Email**: langvoice.official@gmail.com

---

## 🐛 Bug Reports & Feature Requests

Found a bug or have a feature request? We'd love to hear from you!

- **GitHub Issues**: [https://github.com/LangVoice/langvoice-python-sdk/issues](https://github.com/LangVoice/langvoice-python-sdk/issues)
- **Email**: langvoice.official@gmail.com

When reporting bugs, please include:
- Python version
- SDK version (`pip show langvoice`)
- Error message and stack trace
- Minimal code to reproduce the issue

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<p align="center">
  Made with ❤️ by <a href="https://www.langvoice.pro/">LangVoice</a>
</p>

<p align="center">
  <a href="https://www.langvoice.pro/">Website</a> •
  <a href="https://github.com/LangVoice">GitHub</a> •
  <a href="https://www.linkedin.com/company/langvoice">LinkedIn</a>
</p>
