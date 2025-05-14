from django import forms

class DocumentAnalysisForm(forms.Form):
    document = forms.FileField(
        label='Upload Document (.txt, .pdf, .docx, .pptx)',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.txt,.pdf,.docx,.pptx'
        })
    )
    analysis_type = forms.ChoiceField(
        label='Select Analysis Type',
        choices=[
            ('summarize', 'Summarization'),
            ('generate_questions', 'Generate Questions')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
