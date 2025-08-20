from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

class UserCreateForm(UserCreationForm):
    """
    Form for creating a new user with role assignment
    """
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('Admin', 'Admin'), ('Researcher', 'Researcher')],
        required=True,
        help_text="Select the user's role"
    )
    is_staff = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Give access to Django admin panel (automatically enabled for Admin role)"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'is_staff')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Set staff status automatically for Admin role
        role = self.cleaned_data['role']
        if role == 'Admin':
            user.is_staff = True
        else:
            user.is_staff = self.cleaned_data['is_staff']
            
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
    """
    Form for editing existing users
    """
    role = forms.ChoiceField(
        choices=[('Admin', 'Admin'), ('Researcher', 'Researcher')],
        required=True,
        help_text="Select the user's role"
    )
    is_staff = forms.BooleanField(
        required=False,
        help_text="Give access to Django admin panel (automatically enabled for Admin role)"
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
        
        # Set staff status automatically for Admin role
        role = self.cleaned_data['role']
        if role == 'Admin':
            user.is_staff = True
        else:
            user.is_staff = self.cleaned_data['is_staff']
            
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
