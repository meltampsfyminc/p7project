
from django.shortcuts import render, get_object_or_404, redirect
from .models import Gusali
from .forms import GusaliForm

def gusali_list(request):
    gusali = Gusali.objects.all()
    return render(request, 'gusali/gusali_list.html', {'gusali': gusali})

def gusali_detail(request, pk):
    gusali = get_object_or_404(Gusali, pk=pk)
    return render(request, 'gusali/gusali_detail.html', {'gusali': gusali})

def gusali_create(request):
    if request.method == 'POST':
        form = GusaliForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gusali_list')
    else:
        form = GusaliForm()
    return render(request, 'gusali/gusali_form.html', {'form': form})

def gusali_update(request, pk):
    gusali = get_object_or_404(Gusali, pk=pk)
    if request.method == 'POST':
        form = GusaliForm(request.POST, instance=gusali)
        if form.is_valid():
            form.save()
            return redirect('gusali_list')
    else:
        form = GusaliForm(instance=gusali)
    return render(request, 'gusali/gusali_form.html', {'form': form})

def gusali_delete(request, pk):
    gusali = get_object_or_404(Gusali, pk=pk)
    if request.method == 'POST':
        gusali.delete()
        return redirect('gusali_list')
    return render(request, 'gusali/gusali_confirm_delete.html', {'gusali': gusali})
