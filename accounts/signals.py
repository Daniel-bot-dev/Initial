from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from .models import OTP, User
import random
import requests

def generate_otp():

    otp = random.randint(100000, 999999)
    return otp

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.role in ['app_admin', 'user']:
        instance.is_active = True
        instance.save()
        otp = generate_otp()
        expiry_date = timezone.now() + timezone.timedelta(minutes=10)
        OTP.objects.create(
            otp=otp,
            user=instance,
            expiry_date=expiry_date
        )
        url = "https://api.useplunk.com/v1/track"
        header = {
            "Authorization": "Bearer sk_73e20053b8d7740e883642f612bb6cf42c53d79d60bec2fc",
            "Content-Type": "application/json"
        }
        data = {
            "email": instance.email,
            "event": "welcome",
            "data": {
                "full_name": instance.full_name,
                "otp": str(otp)
            }
        }
        response = requests.post(
            url=url,
            headers=header,
            json=data
        )
        print(response.json())



