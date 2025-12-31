from google import genai
from django.conf import settings


def summarize_text(text):
    if not settings.GEMINI_API_KEY:
        return "AI summarization unavailable."

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Summarize the following text:\n{text}"
        )
        return response.text
    except Exception:
        return "AI summarization unavailable due to API restrictions."
