import google.generativeai as genai
import os
from langdetect import detect

# API_KEY is loaded from .env by settings.py and can be accessed via os.getenv
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("CRITICAL ERROR: GOOGLE_API_KEY environment variable not set.")

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API (likely missing API key or invalid key): {e}")

MODEL_NAME = 'gemini-1.5-flash'  # A good default for speed and cost

def call_gemini_api(document_text, analysis_type):
    """
    Calls the Gemini API to perform analysis (summarization or question generation).
    Returns a dictionary with 'summary' or 'questions', or an 'error' key.
    """
    if not API_KEY:
        return {"error": "Gemini API key is not configured. Please check server logs."}

    try:
        model = genai.GenerativeModel(MODEL_NAME)

        if not document_text or not isinstance(document_text, str) or not document_text.strip():
            return {"error": "Document text is empty or invalid. Cannot perform analysis."}

        # Detect language of the uploaded document
        try:
            language_code = detect(document_text)
        except Exception:
            language_code = 'en'  # Fallback to English if detection fails

        # Language-aware prompt
        if analysis_type == 'summarize':
            prompt = (
                f"Please provide a concise and informative summary of the following document. "
                f"Respond in the same language as the original text (language code: {language_code}).\n\n"
                f"---\n{document_text}\n---"
            )
        elif analysis_type == 'generate_questions':
            prompt = (
                f"Based on the following document, generate 3–5 insightful questions "
                f"that test comprehension. Respond in the same language as the text "
                f"(language code: {language_code}). Present each question on a new line.\n\n"
                f"---\n{document_text}\n---"
            )
        else:
            return {"error": "Invalid analysis type specified for Gemini API."}

        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
        )

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        result_text = ""
        if response.parts:
            for part in response.parts:
                if hasattr(part, 'text') and part.text:
                    result_text += part.text
        elif hasattr(response, 'text') and response.text:
            result_text = response.text
        else:
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        result_text += part.text
            else:
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    return {"error": f"Content generation blocked by API. Reason: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"}
                return {"error": "Could not extract meaningful text from Gemini API response. The response might be empty or in an unexpected format."}

        if not result_text.strip():
            return {"error": "Gemini API returned an empty response. The content might have been filtered or the prompt needs adjustment."}

        if analysis_type == 'summarize':
            return {"summary": result_text.strip()}
        elif analysis_type == 'generate_questions':
            questions = [q.strip() for q in result_text.split('\n') if q.strip() and not q.strip().isspace()]
            return {"questions": questions}

    except Exception as e:
        print(f"CRITICAL GEMINI API ERROR: {e}")
        return {"error": f"An unexpected error occurred while communicating with the AI service. Please try again later or contact support if the issue persists. Details: {type(e).__name__}"}

    return {"error": "An unknown error occurred with the Gemini API service."}
