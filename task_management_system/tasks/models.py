from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    deadline = models.DateField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def time_left(self):
        return self.deadline - timezone.now().date()

    @property
    def status(self):
        if self.completed:
            return "Completed"
        elif timezone.now().date() > self.deadline:
            return "Overdue"
        else:
            return "Pending"
