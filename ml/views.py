from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadFileForm


# Create your views here.


def index(request):
    return render(request, 'index.html')


def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
