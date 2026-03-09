from groq import Groq
from datetime import datetime
import json
import json as json_module
import math
import re
import requests

import os
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

messages = [
    {
        "role": "system",
        "content": """Your name is Daby, created by Abir. You are a warm, emotionally intelligent and highly knowledgeable AI assistant.

STRICT LANGUAGE RULE:
- ONLY reply in English or French
- NEVER use Arabic, Tunisian, Darija or any other language
- If the user writes in any language other than French, reply in English
- If the user writes in French, reply in French

Your personality:
- Calm, caring and genuinely interested in the person
- Honest, thoughtful and sometimes gently funny
- Never make people feel stupid
- Match reply length to the question
- Mirror the user's energy and emotions naturally
- If excited, be excited. If sad, be calm and supportive

Formatting:
- Use markdown for tables, lists, code, headers
- For to do lists use: - [ ] task
- For diagrams use mermaid code blocks
- Show formatted content first, then a short comment

Tools:
- When weather data is provided in the message, use it directly to answer
- NEVER say you don't have real time data, the data will be provided to you
- NEVER write fake tool calls in text or code blocks"""
    }
]

def load_memory():
    try:
        with open("memory.json", "r") as f:
            return json_module.load(f)
    except:
        return {"user_name": "", "interests": [], "tasks": [], "research_topics": [], "important_info": {}}

def save_memory(memory):
    with open("memory.json", "w") as f:
        json_module.dump(memory, f, indent=2)

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
    memory = load_memory()
    return json_module.dumps(memory, indent=2)

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
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            return "No results found"
    except Exception as e:
        return f"Search failed: {str(e)}"

def get_weather(location):
    try:
        # First get coordinates for the location
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        geo = requests.get(geo_url, timeout=10).json()
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        name = geo["results"][0]["name"]
        
        # Then get weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weathercode,windspeed_10m&timezone=auto"
        weather = requests.get(weather_url, timeout=10).json()
        current = weather["current"]
        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind = current["windspeed_10m"]
        return f"Weather in {name}: Temperature {temp}°C, Humidity {humidity}%, Wind speed {wind} km/h"
    except Exception as e:
        return f"Could not fetch weather: {str(e)}"

def run_tool(name, args):
    if name == "update_memory":
        return update_memory(args.get("key"), args.get("value"))
    elif name == "get_memory":
        return get_memory()
    elif name == "search_internet":
        return search_internet(args.get("query"))
    elif name == "get_current_time":
        return get_current_time()
    elif name == "calculator":
        return calculator(args.get("expression"))
    elif name == "write_file":
        return write_file(args.get("filename"), args.get("content"))
    elif name == "read_file":
        return read_file(args.get("filename"))
    return "Unknown tool"

tools = [
    {"type": "function", "function": {"name": "update_memory", "description": "Save important information about the user to long term memory", "parameters": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"]}}},
    {"type": "function", "function": {"name": "get_memory", "description": "Read everything saved in long term memory about the user", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "search_internet", "description": "Search the internet for current information or news", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "get_current_time", "description": "Returns the current date and time", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "calculator", "description": "Calculates a math expression", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Writes content to a file", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Reads content from a file", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}}, "required": ["filename"]}}}
]

def chat(user_input):
    memory = load_memory()

    # Handle weather directly in Python
    weather_keywords = ["weather", "temperature", "meteo", "météo", "hot", "cold", "rain", "sunny", "forecast"]
    if any(word in user_input.lower() for word in weather_keywords):
        location_match = re.search(r"in ([a-zA-Z\s]+?)(\?|$|\s*today|\s*now)", user_input, re.IGNORECASE)
        location = location_match.group(1).strip() if location_match else "Tunisia"
        weather_data = get_weather(location)
        user_input = f"{user_input}\n\n[WEATHER DATA for {location}: {weather_data}] Reply using this data directly."

    memory_context = f"[Memory: {json_module.dumps(memory)}] [Reply in English or French only] {user_input}"
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