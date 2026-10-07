from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import FileResponse, Http404
from .models import Memory
from .forms import MemoryForm

def memory_list(request):
    """
    Show list of memories. Template will use memory.is_unlocked property.
    """
    memories = Memory.objects.all()
    authorized_ids = set(request.session.get("unlocked_memories", []))
    for memory in memories:
        memory.has_session_access = memory.pk in authorized_ids
    return render(request, "tcapp/memory_list.html", {"memories": memories})

def memory_create(request):
    """
    Create a memory. The form widget sends a datetime-local string which the form
    parses. Clean method ensures it's future and timezone-aware. We also ensure
    final saved value is aware.
    """
    if request.method == "POST":
        form = MemoryForm(request.POST, request.FILES)
        if form.is_valid():
            mem = form.save(commit=False)
            if timezone.is_naive(mem.unlock_at):
                mem.unlock_at = timezone.make_aware(mem.unlock_at, timezone.get_current_timezone())
            mem.secret_key_hash = make_password(form.cleaned_data["secret_key"])
            mem.save()
            messages.success(request, "Memory saved — it will unlock at the specified time.")
            return redirect("memory_list")
    else:
        form = MemoryForm()
    return render(request, "tcapp/memory_form.html", {"form": form})

def memory_detail(request, pk):
    """
    Show memory content only if unlocked. Server-side guard prevents bypassing.
    """
    memory = get_object_or_404(Memory, pk=pk)
    if not memory.is_unlocked:
        messages.info(request, f"This memory is locked until {memory.unlock_at}.")
        return redirect("memory_list")
    if request.method == "POST":
        secret_key = request.POST.get("secret_key", "")
        # Legacy records have no owner identity to authenticate during an
        # upgrade, so key enrollment must happen through the authenticated admin.
        if not memory.secret_key_hash:
            return render(request, "tcapp/memory_unlock.html", {
                "memory": memory,
                "legacy_key_required": True,
            }, status=403)
        elif not check_password(secret_key, memory.secret_key_hash):
            return render(request, "tcapp/memory_unlock.html", {
                "memory": memory,
                "error": "That key didn’t match. Try again.",
            }, status=403)
        request.session.setdefault("unlocked_memories", [])
        unlocked = request.session["unlocked_memories"]
        if pk not in unlocked:
            unlocked.append(pk)
            request.session["unlocked_memories"] = unlocked
        request.session.set_expiry(600)
        return redirect("memory_detail", pk=pk)
    if pk not in request.session.get("unlocked_memories", []):
        return render(request, "tcapp/memory_unlock.html", {
            "memory": memory,
            "legacy_key_required": not bool(memory.secret_key_hash),
        })
    return render(request, "tcapp/memory_detail.html", {"memory": memory})


def memory_file(request, pk):
    memory = get_object_or_404(Memory, pk=pk)
    if not memory.is_unlocked or pk not in request.session.get("unlocked_memories", []):
        raise Http404
    if not memory.file:
        raise Http404
    return FileResponse(
        memory.file.open("rb"),
        as_attachment=True,
        filename=memory.file.name.rsplit("/", 1)[-1],
        content_type="application/octet-stream",
    )
