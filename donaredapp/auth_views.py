
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm

def registro(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Cuenta creada exitosamente. Bienvenido/a {user.username}!")
            return redirect('donaredapp:index')
        else:
            # Form has errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'donaredapp/registro.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido/a de nuevo, {username}!")
                # Redirect to the page the user was trying to access, or to home
                next_page = request.GET.get('next', 'donaredapp:index')
                return redirect(next_page)
            else:
                messages.error(request, "Usuario o contraseña inválidos.")
        else:
            messages.error(request, "Usuario o contraseña inválidos.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'donaredapp/login.html', {'form': form})

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('donaredapp:index')

@login_required
def perfil(request):
    return render(request, 'donaredapp/perfil.html')