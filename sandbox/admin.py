from django.contrib import admin
from .models import SandboxProgram, SandboxProgramFavorite

@admin.register(SandboxProgram)
class SandboxProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_public', 'share_slug', 'updated_at')
    list_filter = ('is_public',)
    search_fields = ('title', 'description', 'owner__username', 'share_slug')
    readonly_fields = ('share_slug','created_at', 'updated_at')

@admin.register(SandboxProgramFavorite)
class SandboxProgramFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'program', 'created_at')
    search_fields = ('user__username', 'program__title')