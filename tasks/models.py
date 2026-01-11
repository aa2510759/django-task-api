from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
   
    # AbstractUser already includes: username, email, password, etc.
    # Add any custom fields here if needed
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username


class Task(models.Model):
  
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign key to User - equivalent to owner_id in FastAPI
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title