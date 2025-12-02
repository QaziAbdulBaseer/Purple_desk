from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# from .models import YourModel
import requests

def call_main_api(action, instance):
    try:
        requests.get(
            "http://127.0.0.1:8000/api/auth/get-prompt/1/",
        )
    except Exception as e:
        print("Main API error:", e)

@receiver(post_save)
def model_saved(sender, instance, created, **kwargs):
    if created:
        call_main_api("create", instance)
    else:
        call_main_api("update", instance)

@receiver(post_delete)
def model_deleted(sender, instance, **kwargs):
    call_main_api("delete", instance)
