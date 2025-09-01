from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from .models import Memory
from .forms import MemoryForm

def memory_list(request):
    """
    Show list of memories. Template will use memory.is_unlocked property.
    """
    memories = Memory.objects.all()
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
    return render(request, "tcapp/memory_detail.html", {"memory": memory})
