from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )
