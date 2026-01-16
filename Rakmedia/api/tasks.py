# api/tasks.py
from django.conf import settings
from django.core.mail import send_mail


def send_welcome_email_plain(username: str, password: str, email: str):
    """
    Sends a welcome email containing username and password.
    WARNING: sending plaintext passwords is NOT recommended.
    Use temporary password + reset link instead (see below).
    """
    subject = "Welcome — your account details"
    message = f"""
Hello {username},

Your account has been created.

Username: {username}
Password: {password}

Please log in and change your password immediately.
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)


def send_welcome_with_reset_link(username: str, email: str, password_reset_url: str):
    """
    Safer approach: send reset link (one-time or time-limited).
    password_reset_url is the full link which user clicks to set password.
    """
    subject = "Welcome — activate your account / set password"
    message = f"""
Hello {username},

Your account has been created. Please click the link below to set your password:
{password_reset_url}

If you did not request this, ignore this email.
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
