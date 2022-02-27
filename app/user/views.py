from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

import user.models

class RegisterForm(UserCreationForm):
    class Meta:
        model = user.models.User
        fields = ('email', 'password1', 'password2', )


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('shop')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'registration/profile.html'
    models = user.models.User
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, 'Profile updated.')
        return super().form_valid(form)

