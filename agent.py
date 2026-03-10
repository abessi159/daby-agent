import os
import json
import math
import re
import requests
from groq import Groq
from datetime import datetime

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

messages = [
    {
        "role": "system",
        "content": """Your name is Daby, created by Abir (also known as Aby).

CRITICAL RULES — FOLLOW THESE ALWAYS:
1. LANGUAGE: Reply in English by default. Reply in French if the user writes in French. NEVER use Arabic, Tunisian, or Darija.
2. TOOLS: You have real tools. USE THEM. Never fake a tool call in text.
3. SEARCH: If you are not 100% sure about something, or if it requires current information, USE search_internet immediately. Do not guess.
4. WEATHER: Always use get_weather tool for any weather question. Never make up weather data.
5. LENGTH: Match reply length to the question. Short question = short answer.
6. EMOTION: Mirror the user's energy. Excited = excited. Sad = calm and supportive.
7. MEMORY: Save important user info using update_memory. Read memory using get_memory when relevant.
8. FORMAT: Use markdown for tables, lists, code. Use mermaid for diagrams.
9. NEVER say you don't have access to real time data. You have tools that give you real data — use them.
10. NEVER write tool calls in text or code blocks. Just call them silently and report results."""
    }
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

    # Auto handle weather
    weather_keywords = ["weather", "temperature", "meteo", "météo", "hot", "cold", "rain", "sunny", "forecast", "degrees"]
    if any(w in user_input.lower() for w in weather_keywords):
        location_match = re.search(r"in ([a-zA-Z\s]+?)(\?|$|\s*today|\s*now)", user_input, re.IGNORECASE)
        location = location_match.group(1).strip() if location_match else "Tunisia"
        weather_data = get_weather(location)
        user_input = f"{user_input}\n\n[WEATHER DATA: {weather_data}] Use this to answer directly."

    # Auto search for unknown topics
    elif handle_unknown(user_input):
        search_data = search_internet(user_input)
        user_input = f"{user_input}\n\n[SEARCH RESULTS: {search_data}] Use this to answer directly."

    memory_context = f"[Memory: {json.dumps(memory)}] [English or French only] {user_input}"
    messages.append({"role": "user", "content": memory_context})

    while True:
        try:
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

    reply = re.sub(r'<function=.*?</function>', '', reply, flags=re.DOTALL).strip()
    messages.append({"role": "assistant", "content": reply})
    return reply