from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Sum, Q
from django.core.management import call_command
from django.utils.text import get_valid_filename
from io import BytesIO, StringIO
import base64
import os
import uuid
import qrcode

from .models import (
    Property, HousingUnit, PropertyInventory, UserProfile,
    ImportedFile, ItemTransfer, District, Local
)
from .forms import HousingUnitForm


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


# --------------------------------------------------
# Auth
# --------------------------------------------------

def index(request):
    if request.user.is_authenticated:
        return redirect('properties:dashboard')
    return render(request, 'properties/index.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('properties:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        totp_code = request.POST.get('totp_code', '')

        user = authenticate(request, username=username, password=password)
        if not user:
            messages.error(request, 'Invalid credentials')
            return render(request, 'properties/login.html')

        profile, _ = UserProfile.objects.get_or_create(user=user)

        if profile.is_2fa_enabled:
            if not totp_code:
                return render(request, 'properties/login.html', {
                    'show_2fa': True,
                    'username': username,
                    'password': password
                })

            if not profile.verify_totp(totp_code):
                messages.error(request, 'Invalid 2FA code')
                return render(request, 'properties/login.html', {'show_2fa': True})

        login(request, user)
        profile.last_login_ip = get_client_ip(request)
        profile.last_login_date = now()
        profile.save()

        return redirect('properties:dashboard')

    return render(request, 'properties/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('properties:index')


# --------------------------------------------------
# Dashboard
# --------------------------------------------------

@login_required
def dashboard(request):
    return render(request, 'properties/dashboard.html', {
        'housing_units': HousingUnit.objects.count(),
        'inventory_items': PropertyInventory.objects.count(),
        'imported_files': ImportedFile.objects.count(),
        'properties': Property.objects.count(),
        'transfers': ItemTransfer.objects.count(),
        'recent_imports': ImportedFile.objects.all()[:5],
    })


# --------------------------------------------------
# Properties & Housing Units
# --------------------------------------------------

@login_required
def property_list(request):
    properties = Property.objects.all()
    housing_units = HousingUnit.objects.all()

    property_info = []
    for prop in properties:
        property_info.append({
            'id': prop.id,
            'name': prop.name,
            'owner': prop.owner,
            'occupant_count': HousingUnit.objects.filter(property=prop).count()
        })

    return render(request, 'properties/property_list.html', {
        'properties': properties,
        'housing_units': housing_units,
        'property_info': property_info
    })


@login_required
def housing_unit_detail(request, pk):
    housing_unit = get_object_or_404(HousingUnit, pk=pk)
    inventory_items = PropertyInventory.objects.filter(housing_unit=housing_unit)

    return render(request, 'properties/housing_unit_detail.html', {
        'housing_unit': housing_unit,
        'inventory_items': inventory_items
    })


@login_required
def housing_unit_create(request):
    form = HousingUnitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('properties:property_list')

    return render(request, 'properties/housing_unit_form.html', {
        'form': form,
        'title': 'Create Housing Unit'
    })


@login_required
def housing_unit_update(request, pk):
    unit = get_object_or_404(HousingUnit, pk=pk)
    form = HousingUnitForm(request.POST or None, instance=unit)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('properties:housing_unit_detail', pk=pk)

    return render(request, 'properties/housing_unit_form.html', {
        'form': form,
        'title': 'Update Housing Unit'
    })


@login_required
def housing_unit_delete(request, pk):
    unit = get_object_or_404(HousingUnit, pk=pk)

    if request.method == 'POST':
        unit.delete()
        return redirect('properties:property_list')

    return render(request, 'properties/housing_unit_confirm_delete.html', {
        'housing_unit': unit
    })


# --------------------------------------------------
# 🔥 Inventory CRUD
# --------------------------------------------------

@login_required
def inventory_create(request, housing_unit_pk):
    housing_unit = get_object_or_404(HousingUnit, pk=housing_unit_pk)

    if request.method == 'POST':
        PropertyInventory.objects.create(
            housing_unit=housing_unit,
            item_name=request.POST.get('item_name'),
            quantity=request.POST.get('quantity', 1),
            category=request.POST.get('category', ''),
            condition=request.POST.get('condition', 'Good'),
            location=request.POST.get('location', ''),
            remarks=request.POST.get('remarks', '')
        )
        return redirect('properties:housing_unit_detail', pk=housing_unit_pk)

    return render(request, 'properties/inventory_form.html', {
        'housing_unit': housing_unit,
        'title': 'Add Inventory Item'
    })


@login_required
def inventory_update(request, pk):
    item = get_object_or_404(PropertyInventory, pk=pk)

    if request.method == 'POST':
        item.item_name = request.POST.get('item_name')
        item.quantity = request.POST.get('quantity')
        item.category = request.POST.get('category')
        item.condition = request.POST.get('condition')
        item.location = request.POST.get('location')
        item.remarks = request.POST.get('remarks')
        item.save()

        return redirect('properties:housing_unit_detail', pk=item.housing_unit.pk)

    return render(request, 'properties/inventory_form.html', {
        'item': item,
        'title': 'Update Inventory Item'
    })


@login_required
def inventory_delete(request, pk):
    item = get_object_or_404(PropertyInventory, pk=pk)
    unit_pk = item.housing_unit.pk

    if request.method == 'POST':
        item.delete()
        return redirect('properties:housing_unit_detail', pk=unit_pk)

    return render(request, 'properties/inventory_confirm_delete.html', {
        'item': item
    })


# --------------------------------------------------
# Search & Admin Helpers
# --------------------------------------------------

@login_required
def district_search(request):
    q = request.GET.get('q', '')
    districts = District.objects.filter(
        Q(name__icontains=q) | Q(dcode__icontains=q)
    ) if q else District.objects.all()

    return render(request, 'properties/district_search.html', {
        'districts': districts,
        'query': q
    })


@login_required
def district_detail(request, dcode):
    district = get_object_or_404(District, dcode=dcode)
    locals_list = Local.objects.filter(district=district)

    return render(request, 'properties/district_detail.html', {
        'district': district,
        'locals': locals_list
    })


@login_required
def housing_search(request):
    query = request.GET.get('q', '')
    buildings = Property.objects.filter(name__icontains=query) if query else []
    units = HousingUnit.objects.filter(
        occupant_name__icontains=query
    ).select_related('property') if query else []

    return render(request, 'properties/housing_search.html', {
        'query': query,
        'buildings': buildings,
        'units': units
    })
