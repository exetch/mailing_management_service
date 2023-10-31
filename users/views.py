from django.contrib.auth import login, authenticate, models
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import UpdateView, DetailView, FormView, ListView
from .forms import CustomUserLoginForm, ProfileEditForm, CustomUserRegistrationForm
from .models import CustomUser
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetDoneView, PasswordResetCompleteView
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = CustomUserLoginForm

    def form_valid(self, form):
        # Проверяем email и пароль
        username = form.cleaned_data['username']  # Здесь username - это email
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            if user.email_verificated:
                login(self.request, user)
                return super().form_valid(form)
            else:
                # Перенаправляем пользователя на страницу с уведомлением о неподтвержденной почте
                return HttpResponseRedirect(reverse('email_not_verified'))
        else:
            return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    pass

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'users/edit_profile.html'
    def get_success_url(self):
        return reverse_lazy('profile', args=[self.object.pk])

class UserProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'user'


class UserRegistrationView(FormView):
    form_class = CustomUserRegistrationForm
    template_name = 'users/registration_form.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email_verificated = False
        user.save()
        group = models.Group.objects.get(name='Обычный пользователь')
        user.groups.add(group)
        user.save()


        # Отправляем письмо для подтверждения почты
        current_site = get_current_site(self.request)
        mail_subject = 'Подтвердите свой email'
        message = render_to_string('users/verification_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

        return render(self.request, 'users/verification_pending.html')

def email_verification(request, uidb64, token):
    try:
        uid = str(urlsafe_base64_decode(uidb64), 'utf-8')
        user = CustomUser.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.email_verificated = True
            user.save()
            login(request, user)
            return redirect('profile', pk=user.pk)
        else:
            return HttpResponse('Ссылка для подтверждения недействительна.')
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
        return HttpResponse('Ссылка для подтверждения недействительна.')

def email_not_verified(request):
    return render(request, 'users/email_not_verified.html')

class UserPasswordResetView(PasswordResetView):
    email_template_name = 'users/password_reset_email.html'
    template_name = 'users/password_reset_form.html'
    success_url = 'password_reset_done'

class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = 'password_reset_complete'

class PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'  # Шаблон уведомления об успешной отправке инструкций

class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'  # Шаблон уведомления о сбросе пароля

class UsersListView(PermissionRequiredMixin, ListView):
    permission_required = 'users.view_customuser'
    model = CustomUser
    template_name = 'users/users_list.html'

    def get_queryset(self):
        group = models.Group.objects.get(name='Обычный пользователь')

        return CustomUser.objects.filter(groups=group)


def toggle_user_active_status(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    user.is_active = not user.is_active
    user.save()
    return redirect('users_list')