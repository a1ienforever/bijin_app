import base64
from io import BytesIO

import qrcode
from django.contrib.auth import login, get_user_model, get_backends
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice

from users.forms import (
    RegisterUserForm,
    ProfileUserForm,
    UserPasswordChangeForm,
)
from users.models import User


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = "users/login.html"
    extra_context = {"title": "Авторизация"}
    success_url = reverse_lazy("")

    def form_valid(self, form):
        user = form.get_user()
        if user_has_device(user, confirmed=True):
            self.request.session['otp_user_id'] = user.pk
            return redirect('users:otp_login')
        else:
            login(self.request, user)
            return redirect(self.success_url)


def otp_login(request):
    user_id = request.session.get('otp_user_id')

    if not user_id:
        return redirect('users:login')

    user = User.objects.get(pk=user_id)
    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

    if request.method == 'POST':
        token = request.POST.get('token')

        if device and device.verify_token(token):

            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'

            login(request, user, backend=user.backend)

            del request.session['otp_user_id']  # Удаляем ID пользователя из сессии после успешного входа
            return redirect('users:profile')  # Перенаправляем на страницу профиля
        else:
            return render(request, 'users/otp_login.html', {'error': 'Неверный одноразовый код'})

    return render(request, 'users/otp_login.html')


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "users/register.html"
    extra_context = {"title": "Регистрация"}
    success_url = reverse_lazy("users:login")


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = "users/profile.html"
    extra_context = {"title": "Профиль Пользователя"}

    def get_success_url(self):
        return reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"


@login_required
def set_otp(request):
    user = request.user

    qr_code = None
    error_message = None

    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

    if not device:
        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()

        if not device:
            device = TOTPDevice.objects.create(user=user, name="default", confirmed=False)

        uri = device.config_url
        qr = qrcode.make(uri)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        qr_code = buffer

        if request.method == 'POST':
            token = request.POST.get('token')

            if device.verify_token(token):
                device.confirmed = True
                device.save()
                return redirect('users:profile')
            else:
                error_message = 'Неверный код. Попробуйте снова.'

        qr_code = base64.b64encode(qr_code.getvalue()).decode()
        return render(request, 'users/add_otp.html', {
            'qr_code': qr_code,
            'error': error_message,
            'otp_enabled': device and device.confirmed
        })
    else:
        qr_code = device.config_url
        return render(request, 'users/add_otp.html', {
            'qr_code': qr_code,
            'otp_enabled': device and device.confirmed
        })
