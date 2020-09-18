from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm


@login_required
def index(request):
    return render(request, 'index/index.html')


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Entrou com sucesso', extra_tags='success')
                return redirect(reverse('index:index'))
            else:
                messages.error(request, 'Credenciais inválidas. Verifique e tente novamente', extra_tags='danger')
                return render(request, 'index/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'index/login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.success(request, 'Saiu com sucesso', extra_tags='success')
    return redirect(reverse('index:login_user'))
