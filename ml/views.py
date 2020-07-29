from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .forms import ChoiceFileForm
from .forms import UploadFileForm
from .forms import SelectFileForm
from .forms import NumberClusterForm
from .models import UploadFile
from ml.hotspot_predictor import HotspotPredictor


@login_required
def index(request):
    form = ChoiceFileForm()
    return render(request, 'ml/index.html', {'form': form})


@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('ml:index'))
    else:
        form = UploadFileForm()
    return render(request, 'ml/upload.html', {'form': form})


@login_required
def configure(request):
    if request.method == 'POST':
        pks = request.POST.getlist('pk')
        if pks:
            context = {
                'select_form': SelectFileForm(pks),
                'n_clusters_form': NumberClusterForm(),
                'range': range(len(pks))
            }
            return render(request, 'ml/configure.html', context)
    return HttpResponseRedirect(reverse('ml:index'))


@login_required
def delete(request):
    if request.method == 'POST':
        pks = request.POST.getlist('pk')
        if pks:
            files = UploadFile.objects.filter(id__in=pks)
            for file in files:
                file.file.delete(save=True)
                file.delete()
    return HttpResponseRedirect(reverse('ml:index'))


@login_required
def train(request):
    if request.method == 'POST':
        filepaths = request.POST.getlist('filepath')
        n_clusters_form = NumberClusterForm(request.POST)
        if filepaths and n_clusters_form.is_valid():
            n_clusters = n_clusters_form.cleaned_data['n_clusters']
            predictor = HotspotPredictor(filepaths, n_clusters)
            # TODO: salvar os hotspots
    return HttpResponseRedirect(reverse('ml:index'))