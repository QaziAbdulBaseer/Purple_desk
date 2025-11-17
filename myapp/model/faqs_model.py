from django.db import models
from myapp.model.locations_model import Location

class FAQ(models.Model):
    faq_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='faqs')
    question_type = models.CharField(max_length=255, blank=False, null=False)
    question = models.TextField(blank=False, null=False)
    answer = models.TextField(blank=False, null=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'faqs'
        ordering = ['faq_id']
        
    def __str__(self):
        return f"{self.question_type} - {self.location.location_name}"