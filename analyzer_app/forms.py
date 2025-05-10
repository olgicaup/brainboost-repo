from django import forms

class DocumentAnalysisForm(forms.Form):
    # API Key is now handled by environment variable in gemini_service.py
    # If you specifically want users to enter their own key, you can add it back:
    # api_key = forms.CharField(
    #     label='Your Gemini API Key',
    #     widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Gemini API Key'})
    # )
    document = forms.FileField(
        label='Upload Document (.txt, .pdf, .docx)',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    analysis_type = forms.ChoiceField(
        label='Select Analysis Type',
        choices=[('summarize', 'Summarization'), ('generate_questions', 'Generate Questions')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )