# Daby — AI Agent

A full-stack conversational AI agent built with Python, Flask, and the Groq API. Daby features long-term memory, real-time web search, live weather, a responsive chat UI, and is deployed on Render.

**Built by [Abir Abessi](https://github.com/abessi159)**

---


## Features

- Conversational AI powered by Llama 3.3 70B via Groq API
- Long-term memory — remembers user info across sessions using `memory.json`
- Real-time web search via DuckDuckGo
- Live weather data via Open-Meteo API
- Calculator — handles math expressions including `sqrt` and `pi`
- File tools — read and write files
- Multilingual — responds in English or French based on user input
- Mobile responsive UI
- Markdown rendering — tables, lists, code blocks, and Mermaid diagrams

---

## Tech Stack

| Layer      | Technology                      |
|------------|---------------------------------|
| Backend    | Python 3.11 + Flask             |
| AI Model   | Llama 3.3 70B via Groq API      |
| Web Search | DuckDuckGo (ddgs library)       |
| Weather    | Open-Meteo API                  |
| Memory     | JSON file (memory.json)         |
| Frontend   | Vanilla HTML / CSS / JavaScript |
| Markdown   | marked.js + Mermaid.js          |
| Deployment | Render (free tier)              |

---

## Project Structure

```
daby-agent/
├── app.py              # Flask web server
├── agent.py            # AI agent logic, tools, memory
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── memory.json         # Long-term user memory
├── static/
│   └── daby.png        # Avatar image
└── templates/
    └── index.html      # Chat UI
```

---

## How It Works

```
User sends message
      |
Flask receives it (app.py)
      |
Agent decides: use a tool or answer directly? (agent.py)
       |
Tool called if needed (search, weather, calculator...)
       |
Llama 3.3 generates reply using tool results
       |
Reply sent back to browser
```

---

## Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/abessi159/daby-agent.git
cd daby-agent
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set your Groq API key**
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_key_here"
```

**4. Run**
```bash
python app.py
```

**5. Open** `http://localhost:5000`

---

## Available Tools

| Tool             | Description                              |
|------------------|------------------------------------------|
| search_internet  |Search DuckDuckGo for current information |
| get_weather      | Fetch real-time weather for any city     |
| get_current_time | Returns current date and time            |
| calculator       | Evaluates math expressions               |
| write_file       | Saves content to a file                  |
| read_file        | Reads content from a file                |
| update_memory    | Saves user info to long-term memory      |
| get_memory       | Reads saved user memory                  |

---

## Deploy on Render

1. Fork this repo
2. Create a new Web Service on [Render](https://render.com)
3. Connect your GitHub repo
4. Add environment variable: `GROQ_API_KEY` = your Groq key
5. Start command: `gunicorn app:app`
6. Deploy

---

## Known Limitations

- Groq free tier: 100,000 tokens per day
- Render free tier: cold start delay on first message (~50 seconds)
- Memory resets on Render redeploy (no persistent database yet)
- Tool calling reliability depends on the model

---

## Roadmap

- Persistent memory with Supabase or SQLite
- Personality modes (Assistant / Research / Roast)
- Source transparency — show links when searching
- Voice input
- Offline mode with Ollama
- User accounts with separate memory per user

---

## Author

**Abir Abessi** — Software Development student at EPI School, Sousse, Tunisia

- GitHub: [@abessi159](https://github.com/abessi159)

---

## License

MIT License — free to use and modify.
