
from django.shortcuts import render, get_object_or_404, redirect
from .models import Kagamitan
from .forms import KagamitanForm

def kagamitan_list(request):
    kagamitan = Kagamitan.objects.all()
    return render(request, 'kagamitan/kagamitan_list.html', {'kagamitan': kagamitan})

def kagamitan_detail(request, pk):
    kagamitan = get_object_or_404(Kagamitan, pk=pk)
    return render(request, 'kagamitan/kagamitan_detail.html', {'kagamitan': kagamitan})

def kagamitan_create(request):
    if request.method == 'POST':
        form = KagamitanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kagamitan_list')
    else:
        form = KagamitanForm()
    return render(request, 'kagamitan/kagamitan_form.html', {'form': form})

def kagamitan_update(request, pk):
    kagamitan = get_object_or_404(Kagamitan, pk=pk)
    if request.method == 'POST':
        form = KagamitanForm(request.POST, instance=kagamitan)
        if form.is_valid():
            form.save()
            return redirect('kagamitan_list')
    else:
        form = KagamitanForm(instance=kagamitan)
    return render(request, 'kagamitan/kagamitan_form.html', {'form': form})

def kagamitan_delete(request, pk):
    kagamitan = get_object_or_404(Kagamitan, pk=pk)
    if request.method == 'POST':
        kagamitan.delete()
        return redirect('kagamitan_list')
    return render(request, 'kagamitan/kagamitan_confirm_delete.html', {'kagamitan': kagamitan})
