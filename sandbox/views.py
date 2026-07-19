import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import SandboxProgram, SandboxProgramFavorite

@login_required
def sandbox_view(request, pk=None):
    program = None
    if pk is not None:
        program = get_object_or_404(SandboxProgram, pk=pk, owner=request.user)
    return render(request, "sandbox/sandbox.html", {"program": program})

@login_required
def program_list(request):
    query = request.GET.get('q', '').strip()
    programs = request.user.sandbox_programs.annotate(favorites_count=Count('favorited_by', distinct=True))
    if query:
        programs = programs.filter(Q(title__icontains=query) | Q(description__icontains=query))

    favorited_ids = set(
        SandboxProgramFavorite.objects.filter(user=request.user).values_list('program_id', flat=True)
    )
    return render(request, "sandbox/program_list.html", {
        "programs": programs,
        "query": query,
        "favorited_ids": favorited_ids,
    })

@login_required
def program_favorites(request):
    query = request.GET.get('q', '').strip()

    favorites = SandboxProgramFavorite.objects.filter(user=request.user).filter(
        Q(program__is_public=True) | Q(program__owner=request.user)
    ).select_related('program', 'program__owner').order_by('-created_at')

    if query:
        favorites = favorites.filter(
            Q(program__title__icontains=query) |
            Q(program__description__icontains=query) |
            Q(program__owner__username__icontains=query)
        )

    programs = [f.program for f in favorites]
    counts = dict(
        SandboxProgram.objects.filter(id__in=[p.id for p in programs])
        .annotate(favorites_count=Count('favorited_by', distinct=True))
        .values_list('id', 'favorites_count')
    )
    for p in programs:
        p.favorites_count = counts.get(p.id, 0)

    return render(request, "sandbox/program_favorites.html", {
        "programs": programs,
        "query": query,
        "favorited_ids": {p.id for p in programs},
    })

@login_required
def program_gallery(request):
    query = request.GET.get('q', '').strip()
    programs = SandboxProgram.objects.filter(is_public=True).select_related('owner').annotate(
        favorites_count=Count('favorited_by', distinct=True)
    )
    if query:
        programs = programs.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(owner__username__icontains=query)
        )

    favorited_ids = set(
        SandboxProgramFavorite.objects.filter(user=request.user).values_list('program_id', flat=True)
    )
    return render(request, "sandbox/program_gallery.html", {
        "programs": programs,
        "query": query,
        "favorited_ids": favorited_ids,
    })

@login_required
@require_POST
def program_save(request):
    data = json.loads(request.body)
    program_id = data.get("id")
    title = (data.get("title", "Untitled Program")).strip()[:120]
    description = (data.get("description", "")).strip()
    code = data.get("code", "")

    if program_id:
        program = get_object_or_404(SandboxProgram, pk=program_id, owner=request.user)
        program.title = title
        program.description = description
        program.code = code
        program.save()
    else:
        program = SandboxProgram.objects.create(owner=request.user, title=title, description=description, code=code)

    return JsonResponse({"id": program.id, "title": program.title, "description": program.description, "share_slug": program.share_slug, "is_public": program.is_public, })

@login_required
@require_POST
def program_toggle_public(request, pk):
    program = get_object_or_404(SandboxProgram, pk=pk, owner=request.user)
    program.is_public = not program.is_public
    program.save(update_fields=['is_public'])
    return JsonResponse({"is_public": program.is_public})

@login_required
@require_POST
def program_delete(request, pk):
    program = get_object_or_404(SandboxProgram, pk=pk, owner=request.user)
    program.delete()
    return JsonResponse({"deleted": True})

def program_share_view(request, slug):
    program = get_object_or_404(SandboxProgram, share_slug=slug)
    if not program.is_public and program.owner != request.user:
        return HttpResponseForbidden("This program is private.")
    return render(request, "sandbox/program_share.html", {"program": program})

@login_required
@require_POST
def program_favorite_toggle(request, pk):
    program = get_object_or_404(SandboxProgram, pk=pk)
    if not program.is_public and program.owner != request.user:
        return HttpResponseForbidden("This program is private.")

    favorite, created = SandboxProgramFavorite.objects.get_or_create(user=request.user, program=program)
    if not created:
        favorite.delete()

    return JsonResponse({
        "favorited": created,
        "count": program.favorited_by.count(),
    })

@login_required
@require_POST
def program_fork(request, slug):
    source = get_object_or_404(SandboxProgram, share_slug=slug)
    if not source.is_public and source.owner != request.user:
        return HttpResponseForbidden("This program is private.")

    forked = SandboxProgram.objects.create(
        owner=request.user,
        title=f"Fork of {source.title}",
        description=source.description,
        code=source.code
    )
    return JsonResponse({"id": forked.id, "title": forked.title, "share_slug": forked.share_slug, "is_public": forked.is_public})