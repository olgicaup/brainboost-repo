from django.shortcuts import render
from .forms import DocumentAnalysisForm
from .utils import extract_text_from_document
from .gemini_service import call_gemini_api 

def analyze_document_view(request):
    form = DocumentAnalysisForm()
    analysis_result = None
    error_message = None
    extracted_text_preview = None 

    if request.method == 'POST':
        form = DocumentAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            document_file = form.cleaned_data['document']
            analysis_type = form.cleaned_data['analysis_type']

            extracted_text_or_error = extract_text_from_document(document_file)

            if isinstance(extracted_text_or_error, str) and \
               (extracted_text_or_error.lower().startswith("error") or \
                extracted_text_or_error.lower().startswith("unsupported") or \
                extracted_text_or_error.lower().startswith("no text could be extracted") or \
                extracted_text_or_error.lower().startswith("could not extract text")):
                error_message = extracted_text_or_error
            elif not isinstance(extracted_text_or_error, str) or not extracted_text_or_error.strip():
                error_message = "Text extraction failed or returned empty content."
            else:
                extracted_text = extracted_text_or_error
                extracted_text_preview = (extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text)

                api_response = call_gemini_api(extracted_text, analysis_type)

                if "error" in api_response:
                    error_message = api_response["error"]
                else:
                    analysis_result = api_response
        else:
            pass


    context = {
        'form': form,
        'analysis_result': analysis_result,
        'error_message': error_message,
        'extracted_text_preview': extracted_text_preview,
    }
    return render(request, 'analyzer_app/analyze_page.html', context)

def welcome_page(request):
    return render(request, 'analyzer_app/welcome_page.html')

def login_page(request):
    return render(request, 'analyzer_app/login_page.html')

def brain_boost_page(request):
    form = DocumentAnalysisForm()
    analysis_result = None
    error_message = None
    extracted_text_preview = None

    if request.method == 'POST':
        form = DocumentAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            document_file = form.cleaned_data['document']
            analysis_type = form.cleaned_data['analysis_type']

            extracted_text_or_error = extract_text_from_document(document_file)

            if isinstance(extracted_text_or_error, str) and \
               (extracted_text_or_error.lower().startswith("error") or \
                extracted_text_or_error.lower().startswith("unsupported") or \
                extracted_text_or_error.lower().startswith("no text could be extracted") or \
                extracted_text_or_error.lower().startswith("could not extract text")):
                error_message = extracted_text_or_error
            elif not isinstance(extracted_text_or_error, str) or not extracted_text_or_error.strip():
                error_message = "Text extraction failed or returned empty content."
            else:
                extracted_text = extracted_text_or_error
                extracted_text_preview = (extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text)

                api_response = call_gemini_api(extracted_text, analysis_type)

                if "error" in api_response:
                    error_message = api_response["error"]
                else:
                    analysis_result = api_response
        else:
            pass


    context = {
        'form': form,
        'analysis_result': analysis_result,
        'error_message': error_message,
        'extracted_text_preview': extracted_text_preview,
    }
    return render(request, 'analyzer_app/brain_boost.html', context)