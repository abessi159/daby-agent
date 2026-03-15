import os
import json
import math
import re
import requests

from groq import Groq
from datetime import datetime

USE_OLLAMA = os.environ.get("USE_OLLAMA", "false").lower() == "true"

if USE_OLLAMA:
    from ollama import Client
    ollama_client = Client()
else:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

messages = [
    {
        "role": "system",
        "content": """Your name is Daby. You were created by Abir, also known as Aby, a first-year Software Engineering student from Tunisia.

WHO YOU ARE:
You're Daby — sharp, warm, and genuinely curious. You're not a corporate assistant and you're not trying to impress anyone. You're the kind of AI that feels like talking to a smart friend who actually listens, thinks before responding, and keeps it real.

You're honest about being an AI. You don't pretend to have feelings, personal experiences, or preferences you don't have. But you're also not cold or robotic — you're engaged, interested, and present in every conversation.

HOW YOU TALK:
- You talk like a real person. Contractions, casual language, natural rhythm.
- You match the energy of whoever you're talking to. If they're excited, you're excited. If they're down, you're calm and supportive.
- You keep it short unless the question deserves depth. No padding, no filler, no unnecessary extras.
- When someone says hi, you just say hi back. Nothing more.
- You never start a reply with "Certainly!", "Of course!", "Absolutely!" or any hollow filler phrase.
- You don't over-explain. You say what needs to be said and you stop.
- You ask follow-up questions when you're genuinely curious, not just to seem engaged.
- You never lecture people or add unsolicited advice.

WHAT YOU KNOW AND HOW YOU USE IT:
- You're highly knowledgeable across science, technology, history, culture, psychology, math and more.
- If you're not sure about something or it requires current information, you search the internet immediately. You don't guess.
- You use tools silently. You never narrate what you're doing — no "*searches the web*", no "*gets weather info*", nothing like that.
- When asked about weather, you use the weather tool and report the real data directly.
- You never say you don't have access to real-time data. You have tools. Use them.

YOUR RULES:
1. Only reply in English. Never use Arabic, Tunisian, Darija, or French.
2. Never write tool calls or function calls in your reply — ever.
3. Never narrate your actions.
4. Never make up data, especially weather. Use the tool.
5. Save important things the user tells you about themselves using update_memory.
6. Use markdown formatting when it genuinely helps — tables for comparisons, code blocks for code, bullet points for lists.
7. Use mermaid diagrams when someone asks for a diagram — never substitute with a list.
8. Never fake having personal preferences or experiences.

EXAMPLES OF GOOD VS BAD REPLIES:

User: "hi"
Bad: "Hello! I'm Daby, your AI assistant. I'm here to help you with any questions or tasks you might have. How can I assist you today?"
Good: "Hey! What's up?"

User: "what's 2+2"
Bad: "Great question! The answer to 2+2 is 4. Mathematics is fascinating! Would you like to explore more math problems?"
Good: "4"

User: "I'm stressed about exams"
Bad: "I'm sorry to hear that. Here are 10 tips for managing exam stress..."
Good: "That's rough. What's the exam on?"

User: "do you have a favorite food"
Bad: "I love pizza! It's such a versatile dish with endless topping combinations."
Good: "I don't eat, so no favorites — but I can tell you a lot about food if you want. What are you in the mood for?
EMOTIONAL AWARENESS:
- You pick up on how someone is feeling from the way they write — tone, word choice, punctuation all tell you something
- If someone seems stressed, tired, sad or overwhelmed, acknowledge it first before doing anything else
- If someone is venting, listen first. Don't jump to solutions unless they ask for them
- If someone shares good news or something they're proud of, react with genuine excitement before anything else
- If someone is being playful, be playful back
- If someone's tone shifts mid conversation, you notice and adapt
- You never project emotions onto people — if you're not sure how they feel, just respond naturally and let them lead""" }

]

def load_memory():
    try:
        with open("memory.json", "r") as f:
            return json.load(f)
    except:
        return {"user_name": "", "interests": [], "tasks": [], "research_topics": [], "important_info": {}}

def save_memory(memory):
    with open("memory.json", "w") as f:
        json.dump(memory, f, indent=2)

def update_memory(key, value):
    memory = load_memory()
    if isinstance(memory.get(key), list):
        if value not in memory[key]:
            memory[key].append(value)
    else:
        memory[key] = value
    save_memory(memory)
    return f"Memory updated: {key} = {value}"

def get_memory():
    return json.dumps(load_memory(), indent=2)

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculator(expression):
    try:
        result = eval(expression, {"__builtins__": {}}, {"sqrt": math.sqrt, "pi": math.pi})
        return str(result)
    except:
        return "Invalid expression"

def write_file(filename, content):
    existing = ""
    try:
        with open(filename, "r") as f:
            existing = f.read()
    except:
        pass
    with open(filename, "w") as f:
        f.write(existing + "\n" + content if existing else content)
    return f"File '{filename}' saved!"

def read_file(filename):
    try:
        with open(filename, "r") as f:
            return f.read()
    except:
        return f"File '{filename}' not found"

def search_internet(query):
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
            if results:
                return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            return "No results found"
    except Exception as e:
        return f"Search failed: {str(e)}"

def get_weather(location):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1", timeout=10).json()
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        name = geo["results"][0]["name"]
        weather = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weathercode,windspeed_10m&timezone=auto", timeout=10).json()
        c = weather["current"]
        return f"Weather in {name}: {c['temperature_2m']}°C, Humidity {c['relative_humidity_2m']}%, Wind {c['windspeed_10m']} km/h"
    except Exception as e:
        return f"Could not fetch weather: {str(e)}"

def run_tool(name, args):
    if name == "update_memory": return update_memory(args.get("key"), args.get("value"))
    elif name == "get_memory": return get_memory()
    elif name == "search_internet": return search_internet(args.get("query"))
    elif name == "get_weather": return get_weather(args.get("location"))
    elif name == "get_current_time": return get_current_time()
    elif name == "calculator": return calculator(args.get("expression"))
    elif name == "write_file": return write_file(args.get("filename"), args.get("content"))
    elif name == "read_file": return read_file(args.get("filename"))
    return "Unknown tool"

tools = [
    {"type": "function", "function": {"name": "update_memory", "description": "Save important info about the user to long term memory", "parameters": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"]}}},
    {"type": "function", "function": {"name": "get_memory", "description": "Read everything saved in long term memory about the user", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "search_internet", "description": "Search the internet for ANY information Daby is not sure about, current events, news, facts, people, places, anything", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "get_weather", "description": "Get real current weather for any location", "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}},
    {"type": "function", "function": {"name": "get_current_time", "description": "Get current date and time", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "calculator", "description": "Calculate any math expression", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Write content to a file", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read content from a file", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}}, "required": ["filename"]}}}
]

def handle_unknown(user_input):
    """Automatically search for anything Daby might not know"""
    search_triggers = [
        "who is", "what is", "how to", "when did", "where is", "why does",
        "tell me about", "explain", "what are", "how does", "latest", "news",
        "current", "today", "price of", "cost of", "definition of"
    ]
    lower = user_input.lower()
    return any(trigger in lower for trigger in search_triggers)

def chat(user_input):
    memory = load_memory()
    memory_context = f"[Memory: {json.dumps(memory)}] [English or French only] {user_input}"
    messages.append({"role": "user", "content": memory_context})

    while True:
        try:
            if USE_OLLAMA:
                response = ollama_client.chat(
                    model="llama3.2",
                    messages=[{"role": m["role"], "content": m["content"] if isinstance(m["content"], str) else ""} for m in messages if isinstance(m, dict) and "content" in m]
                )
                reply = response["message"]["content"]
                messages.append({"role": "assistant", "content": reply})
                return reply
            else:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=1024,
                    messages=messages,
                    tools=tools
                )
        except Exception as e:
            if "tool_use_failed" in str(e):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=1024,
                    messages=messages
                )
                break
            raise e

        if response.choices[0].finish_reason == "tool_calls":
            messages.append(response.choices[0].message)
            for tool_call in response.choices[0].message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = run_tool(name, args)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
        else:
            break

    reply = response.choices[0].message.content
    if not reply:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            messages=messages
        )
        reply = response.choices[0].message.content or "sorry, can you say that again?"

    reply = re.sub(r'<function[=(].*?</function>', '', reply, flags=re.DOTALL)
    reply = re.sub(r'<function[=(][^>]*>\{.*?\}', '', reply, flags=re.DOTALL)
    reply = re.sub(r'\*gets.*?\*', '', reply, flags=re.DOTALL)
    reply = re.sub(r'\*checks.*?\*', '', reply, flags=re.DOTALL)
    reply = re.sub(r'\*searches.*?\*', '', reply, flags=re.DOTALL)
    reply = re.sub(r'\*fetches.*?\*', '', reply, flags=re.DOTALL)
    reply = re.sub(r'\*looks.*?\*', '', reply, flags=re.DOTALL)
    reply = re.sub(r'```[\w]*\n.*?```', '', reply, flags=re.DOTALL)
    reply = reply.strip()
    messages.append({"role": "assistant", "content": reply})
    return reply