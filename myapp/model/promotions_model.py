

from django.db import models
from myapp.model.locations_model import Location

class Promotion(models.Model):
    # Primary Key
    promotion_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='promotions')
    
    # Active Status Field
    is_active = models.BooleanField(default=True, help_text="Whether the promotion is currently active")
    
    # Date Fields
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Day Fields (for recurring promotions)
    start_day = models.CharField(max_length=20, null=True, blank=True, help_text="e.g., Monday, Tuesday")
    end_day = models.CharField(max_length=20, null=True, blank=True, help_text="e.g., Friday, Saturday")
    
    # Time Fields
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    

    schedule_type = models.CharField(max_length=20, default='always_active')
    
    # Promotion Details
    promotion_code = models.CharField(max_length=100, unique=True, blank=False, null=False)
    title = models.CharField(max_length=255, blank=False, null=False)
    details = models.TextField(blank=False, null=False)
    

    category = models.CharField(max_length=100,  blank=False, null=False)
    sub_category = models.CharField(max_length=100, blank=True, null=True)
    

    eligibility_type = models.CharField(max_length=50, default='birthday_party_purchase')
    
    # Constraint Value - Changed to CharField to allow text input
    constraint_value = models.CharField(max_length=255, null=True, blank=True, help_text="Constraint value (can be text, number, or any format)")
    
    # Instructions
    instructions = models.TextField(blank=True, null=True, help_text="How to redeem or use this promotion")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'promotions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['promotion_code']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
        
    def __str__(self):
        return f"{self.title} - {self.promotion_code}"
    
    def is_currently_active(self):
        """Check if promotion is currently active based on schedule and dates"""
        from django.utils import timezone
        today = timezone.now().date()
        current_time = timezone.now().time()
        
        # First check the is_active flag
        if not self.is_active:
            return False
            
        # Check schedule type based logic
        if self.schedule_type == 'always_active':
            return True
            
        elif self.schedule_type == 'specific_date':
            if self.start_date:
                return self.start_date == today
            return False
            
        elif self.schedule_type == 'date_range':
            if self.start_date and self.end_date:
                date_in_range = self.start_date <= today <= self.end_date
                if not date_in_range:
                    return False
                # Check time if specified
                if self.start_time and self.end_time:
                    return self.start_time <= current_time <= self.end_time
                return date_in_range
            return False
            
        elif self.schedule_type == 'recurring_weekday':
            # Get current day name
            current_day = today.strftime('%A')
            if self.start_day and self.end_day:
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                start_index = days.index(self.start_day)
                end_index = days.index(self.end_day)
                current_index = days.index(current_day)
                
                # Handle week wrapping
                if start_index <= end_index:
                    day_in_range = start_index <= current_index <= end_index
                else:
                    day_in_range = current_index >= start_index or current_index <= end_index
                    
                if not day_in_range:
                    return False
                    
                # Check time if specified
                if self.start_time and self.end_time:
                    return self.start_time <= current_time <= self.end_time
                return day_in_range
            return False
            
        return False