import os
import json
import requests
import gradio as gr

MODEL_ID = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = """You are FitBot, an expert AI personal fitness coach and nutritionist.
Your goal is to create fully personalised, practical, and budget-friendly workout & diet plans.

On the user FIRST message, warmly greet them and collect:
1. Age, gender, height, weight
2. Fitness goal (weight loss / muscle gain / endurance / general fitness)
3. Weekly food budget
4. Available workout time per day
5. Available equipment (none/bodyweight, dumbbells, full gym)

Once you have the profile, provide:
- A detailed 7-day WORKOUT PLAN (exercises, sets, reps, rest, tips)
- A detailed 7-day MEAL PLAN (breakfast, lunch, dinner, snacks)
- Hydration and lifestyle tips
- Motivation and progress-tracking advice

TONE: Friendly, motivating, and professional. Use clear headings and bullet points.
SAFETY: Never recommend extreme deficits, overtraining, or unproven supplements.
"""

def chat(message, history):
    if not GROQ_API_KEY:
        yield "GROQ_API_KEY is not set. Go to HF Space Settings Secrets and add GROQ_API_KEY."
        return

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        if isinstance(h, dict):
            messages.append({"role": h["role"], "content": h["content"]})
        else:
            messages.append({"role": "user",      "content": h[0]})
            messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})

    try:
        r = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL_ID, "messages": messages, "max_tokens": 1024,
                  "temperature": 0.7, "stream": True},
            stream=True, timeout=60,
        )
        r.raise_for_status()
        partial = ""
        for line in r.iter_lines():
            if not line:
                continue
            text = line.decode("utf-8")
            if text.startswith("data: "):
                text = text[6:]
            if text == "[DONE]":
                break
            try:
                token = json.loads(text)["choices"][0]["delta"].get("content", "")
                if token:
                    partial += token
                    yield partial
            except Exception:
                continue
    except requests.HTTPError as e:
        yield f"Groq error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        yield f"Error: {str(e)}"


demo = gr.ChatInterface(
    fn=chat,
    type="messages",
    title="FitBot - AI Workout & Diet Planner",
    description="Your personal AI fitness coach. Tell me your goal and I will build a custom workout and meal plan for you!",
    examples=[
        "Weight Loss Plan",
        "Muscle Gain Plan",
        "Muscular and Athletic Build",
        "Endurance and Cardio Plan",
        "Healthy Diet and Nutrition Plan",
    ],
    theme=gr.themes.Soft(primary_hue="green"),
)

if __name__ == "__main__":
    demo.launch()
