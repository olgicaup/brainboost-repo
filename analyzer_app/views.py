from django.shortcuts import render, redirect
from .forms import DocumentAnalysisForm
from .utils import extract_text_from_document
from .gemini_service import call_gemini_api
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
import os
import uuid
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from .models import FavoriteDocument
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def logout_view(request):
    logout(request)
    return redirect('analyzer_app:welcome')
def signup_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, password=password1)
            login(request, user)
            return redirect('analyzer_app:login')

    return render(request, 'analyzer_app/signup_page.html')

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
@login_required
def favorites_page(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        if file_name:
            FavoriteDocument.objects.create(user=request.user, file_name=file_name)
            return redirect('analyzer_app:favorites')

    favorites = FavoriteDocument.objects.filter(user=request.user)
    return render(request, 'analyzer_app/favorites.html', {'favorites': favorites})

@login_required
def delete_favorite(request, file_id):
    FavoriteDocument.objects.filter(id=file_id, user=request.user).delete()
    return redirect('analyzer_app:favorites')

def download_processed_file(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
    else:
        return HttpResponse("File not found", status=404)

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('analyzer_app:brainboost')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'analyzer_app/login_page.html')

def brain_boost_page(request):
    form = DocumentAnalysisForm()
    analysis_result = None
    error_message = None
    extracted_text_preview = None
    download_url = None

    if request.method == 'POST':
        print("Custom file name received:", request.POST.get('custom_file_name'))
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

                    if analysis_result:
                        if not os.path.exists(settings.MEDIA_ROOT):
                            os.makedirs(settings.MEDIA_ROOT)

                        custom_name = request.POST.get('custom_file_name', '').strip()
                        if custom_name:
                            safe_name = "".join(
                                c for c in custom_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
                            processed_file_name = f"{safe_name}.txt"

                            # Check for duplicates and add number if needed
                            file_path = os.path.join(settings.MEDIA_ROOT, processed_file_name)
                            base_name, ext = os.path.splitext(processed_file_name)
                            counter = 1
                            while os.path.exists(file_path):
                                processed_file_name = f"{base_name}_{counter}{ext}"
                                file_path = os.path.join(settings.MEDIA_ROOT, processed_file_name)
                                counter += 1
                        else:
                            processed_file_name = f"brainboost_result_{uuid.uuid4().hex[:8]}.txt"
                            file_path = os.path.join(settings.MEDIA_ROOT, processed_file_name)
                        processed_file_path = os.path.join(settings.MEDIA_ROOT, processed_file_name)

                        with open(processed_file_path, 'w', encoding='utf-8') as f:
                            if 'summary' in analysis_result:
                                f.write(analysis_result['summary'])
                            elif 'questions' in analysis_result:
                                for question in analysis_result['questions']:
                                    f.write(question + '\n')
                            else:
                                f.write("No summary or questions were generated.")

                        download_url = processed_file_name
                    print("✅ Assigned download_url in brain_boost_page:", download_url)
        else:
            pass


    context = {
        'form': form,
        'analysis_result': analysis_result,
        'error_message': error_message,
        'extracted_text_preview': extracted_text_preview,
        'download_url': download_url,

    }
    return render(request, 'analyzer_app/brain_boost.html', context)
