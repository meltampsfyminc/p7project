from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
import csv
from io import TextIOWrapper
from .models import Item
from .forms import ItemForm

@login_required
def item_list(request):
    items = Item.objects.all()
    context = {'items': items}
    return render(request, 'kagamitan/item_list.html', context)

@login_required
def item_list_by_category(request, category):
    items = Item.objects.filter(location=category)
    context = {'items': items, 'category': category}
    return render(request, 'kagamitan/item_list.html', context)

@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    context = {'item': item}
    return render(request, 'kagamitan/item_detail.html', context)

@login_required
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item created successfully.')
            return redirect('kagamitan:item_list')
    else:
        form = ItemForm()
    return render(request, 'kagamitan/item_form.html', {'form': form, 'title': 'Create Item'})

@login_required
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully.')
            return redirect('kagamitan:item_detail', pk=pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'kagamitan/item_form.html', {'form': form, 'title': 'Update Item'})

@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted successfully.')
        return redirect('kagamitan:item_list')
    return render(request, 'kagamitan/item_confirm_delete.html', {'item': item})

@login_required
def kagamitan_csv_upload(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'No file was uploaded.')
            return redirect('kagamitan:kagamitan_csv_upload')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'This is not a CSV file.')
            return redirect('kagamitan:kagamitan_csv_upload')

        try:
            # Use TextIOWrapper for proper decoding
            decoded_file = TextIOWrapper(csv_file.file, 'utf-8')
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                Item.objects.create(**row)

            messages.success(request, 'CSV file has been uploaded and processed successfully.')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
        
        return redirect('kagamitan:item_list')

    return render(request, 'kagamitan/kagamitan_csv_upload.html')

@login_required
def item_upload(request):
    # This view is a placeholder for the Excel upload functionality
    # Similar to gusali's building_upload
    messages.info(request, "Excel upload for Kagamitan is not yet implemented.")
    return redirect('kagamitan:item_list')

@login_required
def item_report(request):
    # This view is a placeholder for the summary report functionality
    # Similar to gusali's building_report
    items = Item.objects.all()
    total_value = items.aggregate(total=Sum('total_price'))['total'] or 0
    context = {
        'items': items,
        'total_items': items.count(),
        'total_value': total_value,
    }
    return render(request, 'kagamitan/item_report.html', context)