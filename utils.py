
from __future__ import annotations
import json
import requests


# History Normaliser
def normalise_history(history: list) -> list[dict]:
    """
    Convert Gradio chat history to OpenAI-style message dicts.

    Gradio can pass history in two shapes depending on the version:
      - New (Gradio 5): list of dicts with 'role' and 'content' keys
      - Old (Gradio 4): list of [user_str, assistant_str] tuples

    Returns a flat list of {"role": ..., "content": ...} dicts.
    """
    messages = []
    for entry in history:
        if isinstance(entry, dict):
            # Gradio 5 messages format — already correct
            messages.append({"role": entry["role"], "content": entry["content"]})
        else:
            # Gradio 4 tuples format — unpack manually
            user_msg, assistant_msg = entry
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
    return messages


# Groq Streaming Request
def stream_groq(
    api_url: str,
    api_key: str,
    model_id: str,
    messages: list[dict],
    max_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: float = 0.92,
    timeout: int = 60,
):
    """
    Send a streaming chat-completion request to the Groq REST API.

    Yields incremental text chunks (partial assistant reply strings) as they
    arrive from the server-sent event (SSE) stream.

    Parameters
    ----------
    api_url     : Full Groq completions endpoint URL.
    api_key     : Bearer token for authentication.
    model_id    : Groq model identifier string.
    messages    : Conversation history including system prompt.
    max_tokens  : Hard cap on generated tokens.
    temperature : Sampling temperature (0 = greedy, 1 = very random).
    top_p       : Nucleus sampling probability mass cutoff.
    timeout     : Seconds before the HTTP request times out.

    Yields
    ------
    str : Accumulated partial reply text (suitable for Gradio streaming).

    Raises
    ------
    requests.HTTPError : Propagated when the API returns a non-2xx status.
    """
    response = requests.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        },
        json={
            "model":       model_id,
            "messages":    messages,
            "max_tokens":  max_tokens,
            "temperature": temperature,
            "top_p":       top_p,
            "stream":      True,
        },
        stream=True,
        timeout=timeout,
    )
    response.raise_for_status()

    partial = ""
    for raw_line in response.iter_lines():
        if not raw_line:
            continue
        line = raw_line.decode("utf-8")
        if line.startswith("data: "):
            line = line[6:]
        if line == "[DONE]":
            break
        try:
            delta = json.loads(line)["choices"][0]["delta"]
            token = delta.get("content", "")
            if token:
                partial += token
                yield partial
        except (KeyError, json.JSONDecodeError):
            continue


# Input Validator 
def is_blank(text: str) -> bool:
    """Return True if the string is empty or only whitespace."""
    return not text or not text.strip()


# BMI Calculator (utility exposed for future use)

def calculate_bmi(weight_kg: float, height_cm: float) -> tuple[float, str]:
    """
    Calculate BMI and return the numeric value plus WHO category label.

    Parameters
    ----------
    weight_kg : Body weight in kilograms.
    height_cm : Height in centimetres.

    Returns
    -------
    (bmi: float, category: str)
    """
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("Height and weight must be positive numbers.")
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal weight"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"

    return bmi, category


# Calorie Estimator (Mifflin-St Jeor) 
def estimate_tdee(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str = "moderate",
) -> int:
    """
    Estimate Total Daily Energy Expenditure (TDEE) using Mifflin-St Jeor BMR
    multiplied by an activity factor.

    Parameters
    ----------
    weight_kg      : Body weight in kilograms.
    height_cm      : Height in centimetres.
    age            : Age in years.
    gender         : 'male' or 'female' (case-insensitive).
    activity_level : One of 'sedentary', 'light', 'moderate', 'active', 'very_active'.

    Returns
    -------
    int : Estimated daily calorie requirement rounded to nearest integer.
    """
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity_factors = {
        "sedentary":   1.2,
        "light":       1.375,
        "moderate":    1.55,
        "active":      1.725,
        "very_active": 1.9,
    }
    factor = activity_factors.get(activity_level.lower(), 1.55)
    return round(bmr * factor)
