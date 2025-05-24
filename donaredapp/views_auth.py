
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, PasswordRecoveryForm, UserEditForm, ProfileEditForm

def registro(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, f"Cuenta creada exitosamente. Bienvenido/a {user.username}!")
                return redirect('donaredapp:index')
            except Exception as e:
                messages.error(request, 'Error al crear la cuenta. Intenta nuevamente.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'donaredapp/registro.html', {'form': form})

def login_user(request):
    if request.user.is_authenticated:
        # If user is already logged in, redirect to index
        return redirect('donaredapp:index')

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

def recuperapass(request):
    if request.method == 'POST':
        form = PasswordRecoveryForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            # Aquí iría la lógica para enviar un correo de recuperación de contraseña
            messages.success(request, "Se ha enviado un correo para recuperar tu contraseña.")
            return redirect('donaredapp:login')
    else:
        form = PasswordRecoveryForm()  # Use the custom form
    
    return render(request, 'donaredapp/recuperapass.html', {'form': form})

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('donaredapp:index')

@login_required
def perfil(request):
    return render(request, 'donaredapp/perfil.html')

@login_required
def editar_perfil(request):
    # Get the user's profile (it should exist due to your signal)
    profile = request.user.profile
    
    # Initialize forms
    user_form = UserEditForm(instance=request.user)
    profile_form = ProfileEditForm(instance=profile)
    password_form = PasswordChangeForm(request.user)
    
    if request.method == 'POST':
        # Check which form was submitted
        if 'change_profile' in request.POST:
            # Profile update
            user_form = UserEditForm(request.POST, instance=request.user)
            profile_form = ProfileEditForm(request.POST, instance=profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
                return redirect('donaredapp:perfil')
            else:
                messages.error(request, 'Por favor, corrige los errores en el formulario.')
                
        elif 'change_password' in request.POST:
            # Password change
            password_form = PasswordChangeForm(request.user, request.POST)
            
            if password_form.is_valid():
                user = password_form.save()
                # Important: Update session to prevent logout after password change
                update_session_auth_hash(request, user)
                messages.success(request, 'Tu contraseña ha sido cambiada correctamente.')
                return redirect('donaredapp:perfil')
            else:
                messages.error(request, 'Por favor, corrige los errores en la contraseña.')
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    }
    
    return render(request, 'donaredapp/editar_perfil.html', context)