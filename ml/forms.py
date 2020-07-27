from django import forms
from ml.models import UploadFile


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control-file'})
        }


class SelectFileForm(forms.Form):
    def __init__(self, pks, *args, **kwargs):
        super(SelectFileForm, self).__init__(*args, **kwargs)
        files = UploadFile.objects.filter(id__in=pks)
        self.fields['filepath'].choices = [(file.file.path, file.file.name) for file in files]

    filepath = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=''
    )


class NumberClusterForm(forms.Form):
    n_clusters = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Defina o número de agrupamentos',
        required=True,
        initial=2000
    )
