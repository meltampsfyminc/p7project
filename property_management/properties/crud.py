
from django.shortcuts import render, get_object_or_404, redirect
from .models import Property, HousingUnit, PropertyInventory, ItemTransfer, District, Local, DistrictProperty, DistrictInventory, LocalProperty, LocalInventory, UserProfile, BackupCode, ImportedFile
from .forms import PropertyForm, HousingUnitForm, PropertyInventoryForm, ItemTransferForm, DistrictForm, LocalForm, DistrictPropertyForm, DistrictInventoryForm, LocalPropertyForm, LocalInventoryForm, UserProfileForm, BackupCodeForm, ImportedFileForm

# Generic CRUD functions
def _get_model_and_form(model_name):
    models = {
        'property': (Property, PropertyForm),
        'housingunit': (HousingUnit, HousingUnitForm),
        'propertyinventory': (PropertyInventory, PropertyInventoryForm),
        'itemtransfer': (ItemTransfer, ItemTransferForm),
        'district': (District, DistrictForm),
        'local': (Local, LocalForm),
        'districtproperty': (DistrictProperty, DistrictPropertyForm),
        'districtinventory': (DistrictInventory, DistrictInventoryForm),
        'localproperty': (LocalProperty, LocalPropertyForm),
        'localinventory': (LocalInventory, LocalInventoryForm),
        'userprofile': (UserProfile, UserProfileForm),
        'backupcode': (BackupCode, BackupCodeForm),
        'importedfile': (ImportedFile, ImportedFileForm),
    }
    return models.get(model_name)

def generic_list(request, model_name):
    model, _ = _get_model_and_form(model_name)
    items = model.objects.all()
    return render(request, f'properties/{model_name}_list.html', {'items': items})

def generic_detail(request, model_name, pk):
    model, _ = _get_model_and_form(model_name)
    item = get_object_or_404(model, pk=pk)
    return render(request, f'properties/{model_name}_detail.html', {'item': item})

def generic_create(request, model_name):
    model, form_class = _get_model_and_form(model_name)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f'{model_name}_list')
    else:
        form = form_class()
    return render(request, f'properties/generic_form.html', {'form': form, 'model_name': model_name})

def generic_update(request, model_name, pk):
    model, form_class = _get_model_and_form(model_name)
    item = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect(f'{model_name}_list')
    else:
        form = form_class(instance=item)
    return render(request, f'properties/generic_form.html', {'form': form, 'model_name': model_name})

def generic_delete(request, model_name, pk):
    model, _ = _get_model_and_form(model_name)
    item = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect(f'{model_name}_list')
    return render(request, f'properties/generic_confirm_delete.html', {'item': item, 'model_name': model_name})
