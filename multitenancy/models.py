from django.db import models

class TenantRequest(models.Model):
    DATABASE_CHOICES = (
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    company_name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='tenant_logos/')
    primary_color = models.CharField(max_length=7)
    secondary_color = models.CharField(max_length=7)
    
    db_type = models.CharField(max_length=10, choices=DATABASE_CHOICES, default='postgresql')  
    db_name = models.CharField(max_length=63)  
    db_user = models.CharField(max_length=63)
    db_password = models.CharField(max_length=128)  
    db_host = models.CharField(max_length=255, default='localhost')
    db_port = models.IntegerField(default=5432)  
    
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.company_name} - {self.subdomain}"