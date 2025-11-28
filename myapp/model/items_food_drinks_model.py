from django.db import models
from myapp.model.locations_model import Location

class ItemsFoodDrinks(models.Model):
    # Primary Key
    item_id = models.AutoField(primary_key=True)
    
    # Foreign Key to Location
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='food_drink_items')
    
    # Category Fields
    category = models.CharField(max_length=100, blank=False, null=False)
    category_priority = models.IntegerField(default=0, help_text="Priority for category ordering")
    category_type = models.CharField(max_length=100, blank=True, null=True)
    options_type_per_category = models.CharField(max_length=100, blank=True, null=True)
    
    # Item Details
    item = models.CharField(max_length=255, blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=True)
    
    # Additional Information
    additional_instructions = models.TextField(blank=True, null=True)
    
    # T-Shirt Related Fields
    t_shirt_sizes = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated sizes if applicable")
    t_shirt_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Party Package Field
    pitch_in_party_package = models.BooleanField(default=False, help_text="Whether this item is included in party packages")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'items_food_drinks'
        ordering = ['category_priority', 'category', 'item']
        indexes = [
            models.Index(fields=['location', 'category']),
            models.Index(fields=['category']),
            models.Index(fields=['pitch_in_party_package']),
            models.Index(fields=['category_priority']),
        ]
        verbose_name = 'Food Drink Item'
        verbose_name_plural = 'Food Drink Items'
        
    def __str__(self):
        return f"{self.item} - {self.location.location_name}"
    
    def get_t_shirt_sizes_list(self):
        """Convert comma-separated sizes to list"""
        if self.t_shirt_sizes:
            return [size.strip() for size in self.t_shirt_sizes.split(',')]
        return []