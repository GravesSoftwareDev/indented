from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string

def generate_share_slug():
    return get_random_string(10)

class SandboxProgram(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sandbox_programs')
    title = models.CharField(max_length=120, default='Untitled Program')
    description = models.TextField(blank=True, default='')
    code = models.TextField(blank=True, default='')
    share_slug = models.CharField(max_length=16, unique=True, editable=False)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} by {self.owner.username}"
    
    def save(self, *args, **kwargs):
        if not self.share_slug:
            slug = generate_share_slug()
            while SandboxProgram.objects.filter(share_slug=slug).exists():
                slug = generate_share_slug()
            self.share_slug = slug
        super().save(*args, **kwargs)


class SandboxProgramFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sandbox_favorites')
    program = models.ForeignKey(SandboxProgram, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'program']

    def __str__(self):
        return f"{self.user.username} ♥ {self.program.title}"