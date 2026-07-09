from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import User, UserProfile, UserRole
from .forms import (
    LoginForm,
    UserRegistrationForm,
    UserUpdateForm,
    ProfileUpdateForm
)


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                messages.success(
                    request,
                    f'Welcome back, {user.get_full_name() or user.username}! 👋'
                )
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('accounts:login')


@method_decorator(login_required, name='dispatch')
class RegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if not (request.user.is_admin or request.user.is_manager):
            messages.error(request, 'Access denied.')
            return redirect('dashboard:home')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not (request.user.is_admin or request.user.is_manager):
            messages.error(request, 'Access denied.')
            return redirect('dashboard:home')
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                UserProfile.objects.create(user=user)
                messages.success(
                    request,
                    f'User {user.get_full_name()} created successfully! ✅'
                )
                return redirect('accounts:user_list')
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class UserListView(View):
    template_name = 'accounts/user_list.html'

    def get(self, request):
        if not (request.user.is_admin or request.user.is_manager):
            messages.error(request, 'Access denied.')
            return redirect('dashboard:home')

        # Idha "All Workers" page - so default-a Field Workers mattum kaatanum
        role_filter = request.GET.get('role', UserRole.FIELD_WORKER)
        users = User.objects.filter(role=UserRole.FIELD_WORKER).order_by('-created_at')

        context = {
            'users': users,
            'role_filter': role_filter,
            'total_users': users.count(),
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )
        profile_form = ProfileUpdateForm(instance=profile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user_form = UserUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )
        profile_form = ProfileUpdateForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully! ✅')
            return redirect('accounts:profile')
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class UserDetailView(View):
    template_name = 'accounts/user_detail.html'

    def get(self, request, pk):
        if not (request.user.is_admin or request.user.is_manager):
            messages.error(request, 'Access denied.')
            return redirect('dashboard:home')
        user = get_object_or_404(User, pk=pk)
        profile, created = UserProfile.objects.get_or_create(user=user)
        context = {
            'viewed_user': user,
            'profile': profile,
        }
        return render(request, self.template_name, context)
    

class CustomerSignupView(View):
    template_name = 'accounts/customer_signup.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not username or not password1:
            messages.error(request, 'Username and password are required.')
            return render(request, self.template_name)

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, self.template_name)

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return render(request, self.template_name)

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password1,
                role='customer',
            )
            if full_name:
                parts = full_name.split(' ', 1)
                user.first_name = parts[0]
                user.last_name = parts[1] if len(parts) > 1 else ''
            if phone:
                user.phone_number = phone
            user.save()
            UserProfile.objects.create(user=user)

        login(request, user)
        messages.success(request, f'Welcome, {user.get_full_name() or user.username}! Your account is ready.')
        return redirect('dashboard:home')
    
