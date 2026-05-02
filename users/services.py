
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    link = f"http://127.0.0.1:8000/api/v1/auth/verify/{uid}/{token}"

    send_mail(
        "Verify email",
        f"Click: {link}",
        settings.EMAIL_HOST_USER,
        [user.email],
    )
