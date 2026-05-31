from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def clear_guest_mode_on_login(sender, user, request, **kwargs):
    """
    Signal receiver that automatically clears the guest_mode session flag 
    whenever a user successfully logs in.
    """
    if request and request.session.get('guest_mode', False):
        del request.session['guest_mode']
        request.session.modified = True
