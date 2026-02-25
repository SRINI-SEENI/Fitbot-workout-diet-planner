---
title: Personalized Workout Diet Planner
emoji: 💪
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
license: mit
short_description: AI chatbot that creates personalised workout & diet plans
---

# 💪 FitBot — AI-Powered Personalised Workout & Diet Planner

FitBot is a **real-time conversational AI fitness coach** built with Gradio and powered by **LLaMA-3.3-70B** via the Groq API.  
It generates fully customised 7-day workout and meal plans based on the user's personal profile, fitness goals, budget, and available equipment — all through a natural chat interface.

---

## 🎯 Features

| Feature | Description |
|---|---|
| 🤖 Real-time AI responses | Streams responses token-by-token using Groq's ultra-fast inference |
| 🏋️ Personalised workout plans | 7-day plans with exercises, sets, reps, rest times |
| 🥗 Custom meal plans | Budget-friendly, culturally aware 7-day meal schedules |
| 💬 Conversational interface | Follow-up questions, plan adjustments, recipe ideas |
| ⚡ Fast streaming | LLaMA-3.3-70B on Groq (~500 tokens/sec) |
| 🌐 Deployed on HF Spaces | Publicly accessible, no install required |

---

## 🗂️ Project Structure

```
fitbot-workout-diet-planner/
│
├── app.py              # Main Gradio application — entry point
├── config.py           # Centralised configuration (model, params, metadata)
├── prompts.py          # All AI system prompts and goal-specific templates
├── utils.py            # Helper utilities (Groq streaming, BMI, TDEE calculator)
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🧠 How It Works

```
User Message
     │
     ▼
 Gradio ChatInterface  (app.py)
     │
     ▼
 Build conversation  ──▶  [system prompt] + [history] + [user message]
     │
     ▼
 POST https://api.groq.com/openai/v1/chat/completions
     │   model: llama-3.3-70b-versatile
     │   stream: true
     ▼
 Parse SSE stream line by line
     │
     ▼
 Yield partial tokens  ──▶  Gradio streams to browser in real time
```

---

### 4. Run the app
```bash
python app.py
```

Open `http://localhost:7860` in your browser.

---

## 💬 Example Conversation

**User:** Weight Loss Plan  
**FitBot:** Hi! I'm FitBot 👋 Let's build your personalised plan. To get started, could you share:
1. Your age, gender, height, and weight?
2. Your weekly food budget?
3. How much time can you dedicate to working out each day?
4. What equipment do you have access to?

**User:** 22 male, 175cm 80kg, $30/week budget, 45 min/day, bodyweight only  
**FitBot:** Perfect! Here's your personalised plan...

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **UI Framework** | [Gradio 5.9.1](https://gradio.app) — ChatInterface |
| **LLM** | LLaMA-3.3-70B Versatile |
| **Inference Provider** | [Groq API](https://groq.com) — serverless, free tier |
| **Streaming** | Server-Sent Events (SSE) via `requests` |
| **Deployment** | [Hugging Face Spaces](https://huggingface.co/spaces) |
| **Language** | Python 3.11+ |

---

## ⚠️ Disclaimer

FitBot provides AI-generated educational fitness and nutrition guidance only.  
Always consult a qualified healthcare professional or certified fitness trainer before starting any new exercise or diet programme.

