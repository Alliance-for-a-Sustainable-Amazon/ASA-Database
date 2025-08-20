from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# Simplify by including forms directly in this file
class UserCreateForm(UserCreationForm):
    """Form for creating a new user with role assignment"""
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('Admin', 'Admin'), ('Researcher', 'Researcher')],
        required=True,
        help_text="Select the user's role"
    )
    is_staff = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Give access to Django admin panel"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'is_staff')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Set staff status and superuser status automatically for Admin role
        role = self.cleaned_data['role']
        if role == 'Admin':
            user.is_staff = True
            user.is_superuser = True  # Make all admin users superusers
        else:
            user.is_staff = self.cleaned_data['is_staff']
            user.is_superuser = False
            
        if commit:
            user.save()
            # Add user to the selected group
            try:
                group = Group.objects.get(name=role)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
            
        return user
        
class UserEditForm(forms.ModelForm):
    """Form for editing existing users"""
    role = forms.ChoiceField(
        choices=[('Admin', 'Admin'), ('Researcher', 'Researcher')],
        required=True,
        help_text="Select the user's role"
    )
    is_staff = forms.BooleanField(
        required=False,
        help_text="Give access to Django admin panel"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'is_active', 'role', 'is_staff')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Set initial role based on user's group
            admin_group = Group.objects.filter(name='Admin').first()
            researcher_group = Group.objects.filter(name='Researcher').first()
            
            if admin_group in self.instance.groups.all():
                self.fields['role'].initial = 'Admin'
            elif researcher_group in self.instance.groups.all():
                self.fields['role'].initial = 'Researcher'
                
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Set staff status and superuser status automatically for Admin role
        role = self.cleaned_data['role']
        if role == 'Admin':
            user.is_staff = True
            user.is_superuser = True  # Make all admin users superusers
        else:
            user.is_staff = self.cleaned_data['is_staff']
            user.is_superuser = False
            
        if commit:
            user.save()
            # Update user's group
            user.groups.clear()
            try:
                group = Group.objects.get(name=role)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
            
        return user

# Permission check for user management views (now allows both superusers and admins)
def admin_or_superuser_required(view_func):
    """Decorator to ensure only superusers or admins can access user management"""
    actual_decorator = user_passes_test(
        lambda u: u.is_superuser or u.groups.filter(name='Admin').exists()
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

class AdminOrSuperUserRequiredMixin(UserPassesTestMixin):
    """Allow both superusers and admins to access these views"""
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists()
        
    def handle_no_permission(self):
        messages.error(self.request, "You need admin privileges to manage user accounts.")
        return redirect('report_table')  # Redirect to home page

@method_decorator(admin_or_superuser_required, name='dispatch')
class UserListView(ListView):
    """View to list all users"""
    model = User
    template_name = 'butterflies/user_management/user_list.html'
    context_object_name = 'users'
    ordering = ['username']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists()
        return context

@method_decorator(admin_or_superuser_required, name='dispatch')
class UserCreateView(CreateView):
    """View to create a new user"""
    model = User
    form_class = UserCreateForm
    template_name = 'butterflies/user_management/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"User {form.cleaned_data['username']} was created successfully.")
        return super().form_valid(form)

@method_decorator(admin_or_superuser_required, name='dispatch')
class UserUpdateView(UpdateView):
    """View to update an existing user"""
    model = User
    form_class = UserEditForm
    template_name = 'butterflies/user_management/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"User {form.cleaned_data['username']} was updated successfully.")
        return super().form_valid(form)

@method_decorator(admin_or_superuser_required, name='dispatch')
class UserDeleteView(DeleteView):
    """View to delete a user"""
    model = User
    template_name = 'butterflies/user_management/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        messages.success(request, f"User {user.username} was deleted successfully.")
        return super().delete(request, *args, **kwargs)
