import google.generativeai as genai
import os
# from dotenv import load_dotenv # Already loaded in settings.py

# API_KEY is loaded from .env by settings.py and can be accessed via os.getenv
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    # This check is crucial. If the key isn't found, the app shouldn't try to run.
    # In a production app, you might log this error or handle it more gracefully.
    print("CRITICAL ERROR: GOOGLE_API_KEY environment variable not set.")
    # raise ValueError("CRITICAL ERROR: GOOGLE_API_KEY environment variable not set. Please set it before running the application.")
    # For now, we'll let it proceed and it will fail when genai.configure is called if key is missing.

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API (likely missing API key or invalid key): {e}")
    # You might want to prevent the app from starting or disable API features if this fails.


# Choose a model (e.g., 'gemini-1.5-flash', 'gemini-pro')
# Check the Gemini documentation for the latest and most suitable models
MODEL_NAME = 'gemini-1.5-flash' # A good default for speed and cost

def call_gemini_api(document_text, analysis_type):
    """
    Calls the Gemini API to perform analysis (summarization or question generation).
    Returns a dictionary with 'summary' or 'questions', or an 'error' key.
    """
    if not API_KEY: # Double check if API key was loaded
        return {"error": "Gemini API key is not configured. Please check server logs."}

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = ""

        if not document_text or not isinstance(document_text, str) or not document_text.strip():
            return {"error": "Document text is empty or invalid. Cannot perform analysis."}

        if analysis_type == 'summarize':
            prompt = f"Please provide a concise and informative summary of the following document. Focus on the key points and main arguments:\n\n---\n{document_text}\n---"
        elif analysis_type == 'generate_questions':
            prompt = f"Based on the content of the following document, please generate 3-5 insightful questions that would effectively test a reader's understanding of its main topics, arguments, and conclusions. Present each question on a new line:\n\n---\n{document_text}\n---"
        else:
            return {"error": "Invalid analysis type specified for Gemini API."}

        # Generation Configuration (Optional, but good for control)
        generation_config = genai.types.GenerationConfig(
            temperature=0.7, # Controls randomness. Lower for more factual, higher for more creative.
            # max_output_tokens=2048, # Adjust based on expected output length
            # top_p=0.9,
            # top_k=40
        )

        # Safety Settings (Important for responsible AI)
        # Adjust thresholds as needed. BLOCK_ONLY_HIGH is less restrictive.
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

        # Robust response text extraction
        result_text = ""
        if response.parts:
            for part in response.parts:
                if hasattr(part, 'text') and part.text:
                    result_text += part.text
        elif hasattr(response, 'text') and response.text: # Older way or simpler responses
            result_text = response.text
        else:
            # Check candidates if parts is empty or not directly accessible
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        result_text += part.text
            else: # If still no text, there might be an issue or the API blocked the response
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    return {"error": f"Content generation blocked by API. Reason: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"}
                return {"error": "Could not extract meaningful text from Gemini API response. The response might be empty or in an unexpected format."}

        if not result_text.strip():
             return {"error": "Gemini API returned an empty response. The content might have been filtered or the prompt needs adjustment."}


        if analysis_type == 'summarize':
            return {"summary": result_text.strip()}
        elif analysis_type == 'generate_questions':
            # Split questions, ensuring clean output
            questions = [q.strip() for q in result_text.split('\n') if q.strip() and not q.strip().isspace()]
            return {"questions": questions}

    except Exception as e:
        # Log the full error for server-side debugging
        print(f"CRITICAL GEMINI API ERROR: {e}")
        # Provide a more generic error to the user
        return {"error": f"An unexpected error occurred while communicating with the AI service. Please try again later or contact support if the issue persists. Details: {type(e).__name__}"}

    return {"error": "An unknown error occurred with the Gemini API service."}

