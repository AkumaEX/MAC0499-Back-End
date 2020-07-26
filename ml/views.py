# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .forms import UploadFileForm
from .models import UploadFile
from ml.hotspot_predictor import HotspotPredictor


def index(request):
    files = UploadFile.objects.all()
    return render(request, 'ml/index.html', {'files': files})


def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('ml:index'))
    else:
        form = UploadFileForm()
    return render(request, 'ml/upload.html', {'form': form})


def delete(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        file = get_object_or_404(UploadFile, pk=pk)
        file.file.delete(save=True)
        file.delete()
    return HttpResponseRedirect(reverse('ml:index'))


def configure(request):
    if request.method == 'POST':
        pks = request.POST.getlist('pk')
        if pks:
            files = UploadFile.objects.filter(id__in=pks)
            return render(request, 'ml/configure.html', {'files': files, 'range': range(len(files))})
    return HttpResponseRedirect(reverse('ml:index'))


def train(request):
    if request.method == 'POST':
        filepaths = request.POST.getlist('filepath')
        if filepaths:
            predictor = HotspotPredictor(filepaths, 2000)
            print(predictor.get_hotspot())
        else:
            print('fail')
    return HttpResponseRedirect(reverse('ml:index'))
