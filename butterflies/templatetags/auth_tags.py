# auth_tags.py
# Custom template tags for authentication and permissions checks

from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """Check if user is in a specific group"""
    if not user.is_authenticated:
        return False
    try:
        return Group.objects.get(name=group_name) in user.groups.all()
    except Group.DoesNotExist:
        return False
        
@register.filter(name='is_admin')
def is_admin(user):
    """Check if user is admin (superuser or in Admin group)"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        return Group.objects.get(name='Admin') in user.groups.all()
    except Group.DoesNotExist:
        return False
