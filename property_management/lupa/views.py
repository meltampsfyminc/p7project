from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
import csv
from io import TextIOWrapper
from .models import Land
from .forms import LandForm

@login_required
def land_list(request):
    lands = Land.objects.all()
    total_area = lands.aggregate(total=Sum('lot_area'))['total'] or 0
    total_value = lands.aggregate(total=Sum('market_value'))['total'] or 0
    context = {
        'lands': lands,
        'total_lands': lands.count(),
        'total_area': total_area,
        'total_value': total_value,
    }
    return render(request, 'lupa/land_list.html', context)

@login_required
def land_detail(request, pk):
    land = get_object_or_404(Land, pk=pk)
    context = {'land': land}
    return render(request, 'lupa/land_detail.html', context)

@login_required
def land_create(request):
    if request.method == 'POST':
        form = LandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Land created successfully.')
            return redirect('lupa:land_list')
    else:
        form = LandForm()
    return render(request, 'lupa/land_form.html', {'form': form, 'title': 'Create Land'})

@login_required
def land_update(request, pk):
    land = get_object_or_404(Land, pk=pk)
    if request.method == 'POST':
        form = LandForm(request.POST, instance=land)
        if form.is_valid():
            form.save()
            messages.success(request, 'Land updated successfully.')
            return redirect('lupa:land_detail', pk=pk)
    else:
        form = LandForm(instance=land)
    return render(request, 'lupa/land_form.html', {'form': form, 'title': 'Update Land'})

@login_required
def land_delete(request, pk):
    land = get_object_or_404(Land, pk=pk)
    if request.method == 'POST':
        land.delete()
        messages.success(request, 'Land deleted successfully.')
        return redirect('lupa:land_list')
    return render(request, 'lupa/land_confirm_delete.html', {'land': land})

@login_required
def lupa_csv_upload(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'No file was uploaded.')
            return redirect('lupa:lupa_csv_upload')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'This is not a CSV file.')
            return redirect('lupa:lupa_csv_upload')

        try:
            decoded_file = TextIOWrapper(csv_file.file, 'utf-8')
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                Land.objects.create(**row)

            messages.success(request, 'CSV file has been uploaded and processed successfully.')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
        
        return redirect('lupa:land_list')

    return render(request, 'lupa/lupa_csv_upload.html')

@login_required
def land_upload(request):
    messages.info(request, "Excel upload for Lupa is not yet implemented.")
    return redirect('lupa:land_list')

@login_required
def land_report(request):
    lands = Land.objects.all()
    total_value = lands.aggregate(total=Sum('market_value'))['total'] or 0
    total_area = lands.aggregate(total=Sum('lot_area'))['total'] or 0
    context = {
        'lands': lands,
        'total_lands': lands.count(),
        'total_value': total_value,
        'total_area': total_area,
    }
    return render(request, 'lupa/land_report.html', context)