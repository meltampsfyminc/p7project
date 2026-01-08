
from django.shortcuts import render, get_object_or_404, redirect
from .models import Lupa
from .forms import LupaForm

def lupa_list(request):
    lupa = Lupa.objects.all()
    return render(request, 'lupa/lupa_list.html', {'lupa': lupa})

def lupa_detail(request, pk):
    lupa = get_object_or_404(Lupa, pk=pk)
    return render(request, 'lupa/lupa_detail.html', {'lupa': lupa})

def lupa_create(request):
    if request.method == 'POST':
        form = LupaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lupa_list')
    else:
        form = LupaForm()
    return render(request, 'lupa/lupa_form.html', {'form': form})

def lupa_update(request, pk):
    lupa = get_object_or_404(Lupa, pk=pk)
    if request.method == 'POST':
        form = LupaForm(request.POST, instance=lupa)
        if form.is_valid():
            form.save()
            return redirect('lupa_list')
    else:
        form = LupaForm(instance=lupa)
    return render(request, 'lupa/lupa_form.html', {'form': form})

def lupa_delete(request, pk):
    lupa = get_object_or_404(Lupa, pk=pk)
    if request.method == 'POST':
        lupa.delete()
        return redirect('lupa_list')
    return render(request, 'lupa/lupa_confirm_delete.html', {'lupa': lupa})
