from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class Lead(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(
        max_length=255,
        verbose_name="Full Name",
        help_text="Enter the full name of the lead"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
        help_text="Enter a valid email address"
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Phone Number",
        help_text="Enter a valid phone number"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Country"
    )
    timezone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Timezone"
    )
    income_range = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Income Range"
    )
    agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads',
        verbose_name="Assigned Agent"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="General Comment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Validate phone number (E.164 or common international/national formats)
        if self.phone and not re.match(r'^\+?[\d\s\-()]{7,20}$', self.phone):
            raise ValidationError({'phone': "Enter a valid phone number."})

        # Validate email (Django's EmailField already does basic validation, but you can add more if needed)
        if self.email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', self.email):
            raise ValidationError({'email': "Enter a valid email address."})

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Lead"
        verbose_name_plural = "Leads"

class LeadComment(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=10, choices=[('agent', 'Agent'), ('manager', 'Manager')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)