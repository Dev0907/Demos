import google.generativeai as genai
from backend.config import GEMINI_API_KEY, GEMINI_MODEL_NAME
import json

genai.configure(api_key=GEMINI_API_KEY)

# Use the requested model
model = genai.GenerativeModel(GEMINI_MODEL_NAME)

def generate_text(prompt: str):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating text: {e}")
        return "I'm sorry, I encountered an error generating the response."

def generate_json(prompt: str):
    try:
        # Force JSON structure in prompt
        json_prompt = f"{prompt}\n\nReturn the result as a valid JSON object. Do not include markdown formatting like ```json."
        response = model.generate_content(json_prompt)
        text = response.text.strip()
        # Clean up if model adds markdown
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text)
    except Exception as e:
        print(f"Error generating JSON: {e}")
        return {}
