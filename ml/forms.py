from django import forms
from ml.models import UploadFile


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control-file'})
        }
