from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from django.contrib import messages
from django.utils.timezone import now
import qrcode
from io import BytesIO
import base64

from admin_core.models import Worker
from admin_core.services.sync import run_admin_core_sync
from gusali.models import Building
from .models import Pamayanan, HousingUnit, HousingUnitInventory, UserProfile, ImportedFile, ItemTransfer, District, Local
from django.db.models import Sum, Q, Count
from django.core.management import call_command
import os
from io import StringIO
import uuid
from django.utils.text import get_valid_filename
from .forms import HousingUnitForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import District, Local
from .forms import DistrictForm, LocalForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def index(request):
    """Homepage/landing page"""
    if request.user.is_authenticated:
        return redirect('properties:dashboard')
    return render(request, 'properties/index.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view with optional 2FA"""
    if request.user.is_authenticated:
        return redirect('properties:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        totp_code = request.POST.get('totp_code', '')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user has 2FA enabled
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
            
            if profile.is_2fa_enabled:
                # Verify TOTP code if provided
                if not totp_code:
                    # Show 2FA form
                    return render(request, 'properties/login.html', {
                        'username': username,
                        'password': password,  # Pass password back for the hidden field
                        'show_2fa': True,
                        'message': 'Enter your 2FA code'
                    })
                
                # Verify TOTP
                totp_valid = profile.verify_totp(totp_code)
                backup_valid = profile.use_backup_code(totp_code) if not totp_valid else False
                
                if not (totp_valid or backup_valid):
                    # Invalid code
                    return render(request, 'properties/login.html', {
                        'username': username,
                        'password': password,  # Pass password back
                        'show_2fa': True,
                        'error': 'Invalid 2FA code or backup code'
                    })
                
                # Valid 2FA code
                login(request, user)
                profile.last_login_ip = get_client_ip(request)
                profile.last_login_date = now()
                profile.save()
                messages.success(request, 'Logged in successfully!')
                return redirect('properties:dashboard')
            else:
                # No 2FA, log in directly
                login(request, user)
                profile.last_login_ip = get_client_ip(request)
                profile.last_login_date = now()
                profile.save()
                messages.success(request, 'Logged in successfully!')
                return redirect('properties:dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'properties/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'properties/login.html')


@login_required(login_url='properties:login')
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('properties:index')


@login_required(login_url='properties:login')
def dashboard(request):
    """User dashboard with overview and statistics"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    # Get statistics
    housing_units = HousingUnit.objects.count()
    inventory_items = HousingUnitInventory.objects.count()
    imported_files = ImportedFile.objects.count()
    properties = Pamayanan.objects.count()
    
    # Get transfer statistics
    transfers = ItemTransfer.objects.count()
    
    # Get recent imports
    recent_imports = ImportedFile.objects.all()[:5]
    
    context = {
        'profile': profile,
        'housing_units': housing_units,
        'inventory_items': inventory_items,
        'imported_files': imported_files,
        'properties': properties,
        'transfers': transfers,
        'recent_imports': recent_imports,
    }
    return render(request, 'properties/dashboard.html', context)


@login_required(login_url='properties:login')
def setup_2fa(request):
    """Setup 2FA for user account"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate':
            # Generate new TOTP secret
            profile.generate_totp_secret()
            profile.save()
        
        elif action == 'verify':
            # Verify TOTP code and enable 2FA
            totp_code = request.POST.get('totp_code', '')
            
            if profile.verify_totp(totp_code):
                profile.is_2fa_enabled = True
                profile.generate_backup_codes()
                profile.save()
                messages.success(request, '2FA has been enabled successfully!')
                return redirect('properties:view_backup_codes')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
        
        elif action == 'disable':
            # Disable 2FA
            if profile.is_2fa_enabled:
                profile.is_2fa_enabled = False
                profile.totp_secret = ''
                profile.backup_codes = ''
                profile.save()
                messages.success(request, '2FA has been disabled.')
                return redirect('properties:dashboard')
    
    # Generate QR code if secret exists
    qr_code_image = None
    if profile.totp_secret:
        qr_uri = profile.get_totp_uri()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_image = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'profile': profile,
        'qr_code_image': qr_code_image,
        'totp_secret': profile.totp_secret,
    }
    return render(request, 'properties/setup_2fa.html', context)


@login_required(login_url='properties:login')
def view_backup_codes(request):
    """View and manage backup codes"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    backup_codes = profile.backup_codes.split(',') if profile.backup_codes else []
    
    context = {
        'backup_codes': backup_codes,
    }
    return render(request, 'properties/backup_codes.html', context)


@login_required(login_url='properties:login')
def property_list(request):
    """Display list of properties and housing units."""
    properties = Pamayanan.objects.all()
    housing_units = HousingUnit.objects.all()
    
    # Get properties with their occupant counts
    property_info = []
    for prop in properties:
        count = HousingUnit.objects.filter(property=prop).count()
        property_info.append({
            'id': prop.id,
            'name': prop.name,
            'owner': prop.owner,
            'occupant_count': count
        })
    
    context = {
        'properties': properties,
        'housing_units': housing_units,
        'property_info': property_info,
    }
    return render(request, 'properties/property_list.html', context)


@login_required(login_url='properties:login')
def inventory_list(request):
    inventory_items = HousingUnitInventory.objects.select_related('housing_unit').all()

    housing_unit_id = request.GET.get('housing_unit')

    selected_unit = None
    if housing_unit_id:
        try:
            selected_unit = int(housing_unit_id)
            inventory_items = inventory_items.filter(housing_unit_id=selected_unit)
        except ValueError:
            selected_unit = None

    housing_units = HousingUnit.objects.all()

    context = {
        'inventory_items': inventory_items,
        'housing_units': housing_units,
        'selected_unit': selected_unit,
    }
    return render(request, 'properties/inventory_list.html', context)


@login_required(login_url="properties:login")
def upload_file(request):
    """
    Handle file upload, import inventory,
    and automatically sync to admin_core.
    """

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return JsonResponse(
                {"success": False, "message": "No file provided"},
                status=400,
            )

        # -------------------------------------------------
        # Validate extension
        # -------------------------------------------------
        allowed_extensions = [".xls", ".xlsx"]
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        if ext not in allowed_extensions:
            return JsonResponse(
                {
                    "success": False,
                    "message": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}",
                },
                status=400,
            )

        # -------------------------------------------------
        # Save file safely
        # -------------------------------------------------
        uploads_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "uploads",
        )
        os.makedirs(uploads_dir, exist_ok=True)

        safe_name = get_valid_filename(uploaded_file.name)
        unique_name = f"{uuid.uuid4().hex[:8]}-{safe_name}"
        file_path = os.path.join(uploads_dir, unique_name)

        try:
            with open(file_path, "wb+") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": f"Failed to save file: {e}",
                },
                status=500,
            )

        # -------------------------------------------------
        # Run inventory import
        # -------------------------------------------------
        output = StringIO()

        try:
            call_command(
                "import_inventory",
                file_path,
                stdout=output,
                stderr=output,
            )
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": f"Import failed: {e}",
                },
                status=500,
            )

        output_text = output.getvalue()

        # -------------------------------------------------
        # Duplicate detection
        # -------------------------------------------------
        if "FILE ALREADY IMPORTED" in output_text:
            return JsonResponse(
                {
                    "success": False,
                    "message": "File already imported.",
                    "details": output_text,
                },
                status=409,
            )

        # -------------------------------------------------
        # Import success → trigger admin_core sync
        # -------------------------------------------------
        if "IMPORT COMPLETE" in output_text:
            try:
                sync_run = run_admin_core_sync(
                    source="properties_upload",
                    triggered_by=request.user.username,
                )
            except Exception as e:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Import succeeded but sync failed.",
                        "details": str(e),
                    },
                    status=500,
                )

            return JsonResponse(
                {
                    "success": True,
                    "message": "File imported and Admin Core synced successfully.",
                    "details": output_text,
                    "sync": {
                        "sync_run_id": sync_run.id,
                        "status": sync_run.status,
                        "conflicts": sync_run.conflicts_detected,
                    },
                }
            )

        # -------------------------------------------------
        # Partial / error case
        # -------------------------------------------------
        return JsonResponse(
            {
                "success": False,
                "message": "Import completed with errors.",
                "details": output_text,
            },
            status=400,
        )

    # -----------------------------------------------------
    # GET → upload page
    # -----------------------------------------------------
    imported_files = ImportedFile.objects.all().order_by("-imported_at")

    return render(
        request,
        "properties/upload_file.html",
        {
            "imported_files": imported_files,
        },
    )


@login_required(login_url='properties:login')
def import_history(request):
    """Display import history"""
    imported_files = ImportedFile.objects.all().order_by('-imported_at')
    
    context = {
        'imported_files': imported_files,
    }
    return render(request, 'properties/import_history.html', context)


@login_required(login_url='properties:login')
def housing_unit_detail(request, pk):
    """Display details of a specific housing unit and its inventory"""
    try:
        housing_unit = HousingUnit.objects.get(pk=pk)
    except HousingUnit.DoesNotExist:
        return render(request, 'properties/404.html', status=404)
    
    inventory_items = HousingUnitInventory.objects.filter(housing_unit=housing_unit)
    
    context = {
        'housing_unit': housing_unit,
        'inventory_items': inventory_items,
    }
    return render(request, 'properties/housing_unit_detail.html', context)


@login_required(login_url='properties:login')
def building_occupants(request, property_id):
    """Display all occupants in a specific property/building"""
    # Get the property
    property_obj = get_object_or_404(Pamayanan, id=property_id)
    
    # Get all housing units in the property
    housing_units = HousingUnit.objects.filter(property=property_obj).order_by('housing_unit_name')
    
    # Get statistics
    total_occupants = housing_units.count()
    departments = housing_units.values_list('department', flat=True).distinct()
    total_departments = len(departments)
    
    context = {
        'property': property_obj,
        'building_name': property_obj.name,
        'housing_units': housing_units,
        'total_occupants': total_occupants,
        'total_departments': total_departments,
        'departments': departments,
    }
    return render(request, 'properties/building_occupants.html', context)


@login_required(login_url='properties:login')
def transfer_list(request):
    """Display list of all item transfers"""
    transfers = ItemTransfer.objects.select_related('inventory_item', 'from_unit', 'to_unit').all()
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        transfers = transfers.filter(status=status)
    
    # Filter by transfer type if specified
    transfer_type = request.GET.get('type')
    if transfer_type:
        transfers = transfers.filter(transfer_type=transfer_type)
    
    # Get statistics
    total_transfers = ItemTransfer.objects.count()
    pending_received = ItemTransfer.objects.filter(received_date__isnull=True).count()
    good_condition = ItemTransfer.objects.filter(status='good').count()
    damaged_items = ItemTransfer.objects.filter(status__in=['damaged', 'broken']).count()
    
    context = {
        'transfers': transfers,
        'total_transfers': total_transfers,
        'pending_received': pending_received,
        'good_condition': good_condition,
        'damaged_items': damaged_items,
        'selected_status': status,
        'selected_type': transfer_type,
    }
    return render(request, 'properties/transfer_list.html', context)


@login_required(login_url='properties:login')
@require_http_methods(["GET", "POST"])
def transfer_create(request):
    """Create a new item transfer with inventory adjustment"""
    if request.method == 'POST':
        try:
            inventory_item_id = request.POST.get('inventory_item')
            transfer_type = request.POST.get('transfer_type')
            from_unit_id = request.POST.get('from_unit')
            to_unit_id = request.POST.get('to_unit')
            to_storage = request.POST.get('to_storage') == 'on'
            transferred_by = request.POST.get('transferred_by')
            receiver_name = request.POST.get('receiver_name')
            received_date = request.POST.get('received_date')
            status = request.POST.get('status', 'good')
            reason = request.POST.get('reason')
            remarks = request.POST.get('remarks')
            quantity = int(request.POST.get('quantity', 1))
            
            # Get the inventory item from source unit
            inventory_item = HousingUnitInventory.objects.get(id=inventory_item_id)
            
            # Validate quantity
            if quantity > inventory_item.quantity:
                messages.error(request, f'Cannot transfer {quantity} units. Only {inventory_item.quantity} available.')
                return redirect('properties:transfer_create')
            
            # STEP 1: Reduce quantity from source unit
            inventory_item.quantity -= quantity
            inventory_item.save()
            
            # STEP 2: Handle destination - either add to destination unit or to storage
            if to_storage:
                # Item goes to storage/bodega - don't create new inventory record
                # Just track the transfer
                pass
            elif to_unit_id:
                # Item goes to another unit
                to_unit = HousingUnit.objects.get(id=to_unit_id)
                
                # Check if this item already exists in the destination unit
                existing_item = HousingUnitInventory.objects.filter(
                    housing_unit=to_unit,
                    item_name=inventory_item.item_name
                ).first()
                
                if existing_item:
                    # Add to existing item
                    existing_item.quantity += quantity
                    existing_item.save()
                else:
                    # Create new inventory record in destination unit
                    # Copy the item details but with new unit and quantity
                    new_item = HousingUnitInventory(
                        housing_unit=to_unit,
                        item_code=inventory_item.item_code,
                        date_acquired=inventory_item.date_acquired,
                        quantity=quantity,
                        item_name=inventory_item.item_name,
                        brand=inventory_item.brand,
                        model=inventory_item.model,
                        make=inventory_item.make,
                        color=inventory_item.color,
                        size=inventory_item.size,
                        serial_number=inventory_item.serial_number,
                        remarks=inventory_item.remarks,
                    )
                    new_item.save()
            
            # STEP 3: Create the transfer record
            transfer = ItemTransfer(
                inventory_item=inventory_item,
                transfer_type=transfer_type,
                from_unit_id=from_unit_id if from_unit_id else None,
                to_unit_id=to_unit_id if to_unit_id else None,
                to_storage=to_storage,
                transferred_by=transferred_by,
                receiver_name=receiver_name,
                received_date=received_date if received_date else None,
                status=status,
                reason=reason,
                remarks=remarks,
                quantity=quantity,
            )
            transfer.save()
            
            messages.success(request, f'Item transfer created successfully! Inventory updated.')
            return redirect('properties:transfer_detail', pk=transfer.id)
        except HousingUnitInventory.DoesNotExist:
            messages.error(request, 'Inventory item not found')
            return redirect('properties:transfer_create')
        except HousingUnit.DoesNotExist:
            messages.error(request, 'Destination unit not found')
            return redirect('properties:transfer_create')
        except ValueError:
            messages.error(request, 'Invalid quantity entered')
            return redirect('properties:transfer_create')
        except Exception as e:
            messages.error(request, f'Error creating transfer: {str(e)}')
            return redirect('properties:transfer_create')
    
    # GET request - show form
    inventory_items = HousingUnitInventory.objects.select_related('housing_unit').all()
    housing_units = HousingUnit.objects.all()
    
    context = {
        'inventory_items': inventory_items,
        'housing_units': housing_units,
    }
    return render(request, 'properties/transfer_create.html', context)


@login_required(login_url='properties:login')
def transfer_detail(request, pk):
    """Display details of a specific transfer"""
    try:
        transfer = ItemTransfer.objects.select_related('inventory_item', 'from_unit', 'to_unit').get(pk=pk)
    except ItemTransfer.DoesNotExist:
        messages.error(request, 'Transfer not found')
        return redirect('properties:transfer_list')
    
    context = {
        'transfer': transfer,
    }
    return render(request, 'properties/transfer_detail.html', context)


@login_required(login_url='properties:login')
def transfer_history(request):
    """Display transfer history with filtering"""
    transfers = ItemTransfer.objects.select_related('inventory_item', 'from_unit', 'to_unit').all()
    
    # Filter by inventory item if specified
    inventory_item_id = request.GET.get('item')
    if inventory_item_id:
        transfers = transfers.filter(inventory_item_id=inventory_item_id)
    
    # Get all inventory items for filter dropdown
    inventory_items = HousingUnitInventory.objects.all()
    
    context = {
        'transfers': transfers,
        'inventory_items': inventory_items,
        'selected_item': inventory_item_id,
    }
    return render(request, 'properties/transfer_history.html', context)

@login_required
def district_search(request):
    """Search engine for Districts"""
    query = request.GET.get('q', '').strip()
    districts = District.objects.all()
    if query:
        districts = districts.filter(Q(name__icontains=query) | Q(dcode__icontains=query))
    
    context = {'districts': districts, 'query': query}
    return render(request, 'properties/district_search.html', context)

@login_required
def district_detail(request, dcode):
    """View locals within a district"""
    district = get_object_or_404(District, dcode=dcode)
    locals_list = Local.objects.filter(district=district).order_by('name')
    context = {
        'district': district,
        'locals': locals_list
    }
    return render(request, 'properties/district_detail.html', context)

@login_required
def local_summary(request, lcode):
    """Aggregate summary for a specific Local across all National apps"""
    from gusali.models import Building
    from kagamitan.models import Item
    from lupa.models import Land
    from plants.models import Plant
    
    local = get_object_or_404(Local, lcode=lcode)
    
    # Cost Summaries
    gusali_cost = Building.objects.filter(local=local).aggregate(total=Sum('current_total_cost'))['total'] or 0
    kagamitan_cost = Item.objects.filter(local=local).aggregate(total=Sum('total_price'))['total'] or 0
    lupa_cost = Land.objects.filter(local=local).aggregate(total=Sum('market_value'))['total'] or 0
    plants_cost = Plant.objects.filter(local=local).aggregate(total=Sum('total_value'))['total'] or 0
    
    total_local_cost = gusali_cost + kagamitan_cost + lupa_cost + plants_cost
    
    context = {
        'local': local,
        'gusali_cost': gusali_cost,
        'kagamitan_cost': kagamitan_cost,
        'lupa_cost': lupa_cost,
        'plants_cost': plants_cost,
        'total_local_cost': total_local_cost,
    }
    return render(request, 'properties/local_summary.html', context)

@login_required
def housing_search(request):
    query = request.GET.get('q', '').strip()

    buildings = []
    units = []

    if query:
        # Search buildings by name only
        buildings = Pamayanan.objects.filter(name__icontains=query)

        # Search workers / occupants by name only
        units = HousingUnit.objects.select_related('property') \
            .filter(occupant_name__icontains=query)

    return render(request, 'properties/housing_search.html', {
        'query': query,
        'buildings': buildings,
        'units': units,
    })
@login_required
def building_map(request, pk):
    """Visualizes housing units in a grid layout (Map-like table)"""
    building = get_object_or_404(Pamayanan, pk=pk)
    # Get units and group by Floor/Unit Number
    units_list = HousingUnit.objects.filter(property=building).order_by('floor', 'housing_unit_name')
    
    # Organize into a grid dictionary {floor: [units]}
    grid = {}
    for unit in units_list:
        floor = unit.floor or "Other"
        if floor not in grid:
            grid[floor] = []
        grid[floor].append(unit)
    
    # Prepare sorted list of tuples [(floor, [units])] for template
    sorted_floors = sorted(grid.keys(), reverse=True)
    floor_data = []
    for floor in sorted_floors:
        floor_data.append((floor, grid[floor]))
    
    context = {
        'building': building,
        'floor_data': floor_data,
    }
    return render(request, 'properties/building_map.html', context)

@login_required
def housing_unit_create(request):
    if request.method == 'POST':
        form = HousingUnitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('properties:property_list')
    else:
        form = HousingUnitForm()
    return render(request, 'properties/housing_unit_form.html', {'form': form, 'title': 'Create Housing Unit'})

@login_required
def housing_unit_update(request, pk):
    housing_unit = get_object_or_404(HousingUnit, pk=pk)
    if request.method == 'POST':
        form = HousingUnitForm(request.POST, instance=housing_unit)
        if form.is_valid():
            form.save()
            return redirect('properties:housing_unit_detail', pk=pk)
    else:
        form = HousingUnitForm(instance=housing_unit)
    return render(request, 'properties/housing_unit_form.html', {'form': form, 'title': 'Update Housing Unit'})

@login_required
def housing_unit_delete(request, pk):
    housing_unit = get_object_or_404(HousingUnit, pk=pk)
    if request.method == 'POST':
        housing_unit.delete()
        return redirect('properties:property_list')
    return render(request, 'properties/housing_unit_confirm_delete.html', {'housing_unit': housing_unit})


@login_required
def district_list(request):
    # Get all districts
    districts_list = District.objects.all().order_by('dcode')
    
    # Pagination - 10 items per page
    paginator = Paginator(districts_list, 10)
    page = request.GET.get('page')
    
    try:
        districts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        districts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        districts = paginator.page(paginator.num_pages)
    
    # Get totals for statistics
    total_locals = Local.objects.count()
    total_buildings = Building.objects.count()
    total_workers = Worker.objects.count()
    
    context = {
        'districts': districts,
        'total_locals': total_locals,
        'total_buildings': total_buildings,
        'total_workers': total_workers,
    }
    
    return render(request, 'properties/district_list.html', context)


@login_required
def district_create(request):
    form = DistrictForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("properties:district_list")

    return render(
        request,
        "properties/district_form.html",
        {
            "form": form,
            "title": "Add District"
        }
    )


@login_required
def district_update(request, dcode):
    district = get_object_or_404(District, dcode=dcode)

    form = DistrictForm(request.POST or None, instance=district)
    if form.is_valid():
        form.save()
        return redirect("properties:district_list")

    return render(
        request,
        "properties/district_form.html",
        {
            "form": form,
            "title": f"Edit District ({district.dcode})",
        }
    )

@login_required
def local_list(request):
    locals = Local.objects.select_related("district").order_by("district__name", "name")
    return render(request, "properties/local_list.html", {"locals": locals})


@login_required
def local_create(request):
    form = LocalForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("properties:local_list")
    return render(request, "properties/local_form.html", {"form": form, "title": "Add Local"})


@login_required
def local_update(request, pk):
    local = get_object_or_404(Local, pk=pk)
    form = LocalForm(request.POST or None, instance=local)
    if form.is_valid():
        form.save()
        return redirect("properties:local_list")
    return render(request, "properties/local_form.html", {"form": form, "title": "Edit Local"})


@login_required
def get_next_lcode(request):
    district_id = request.GET.get("district")

    if not district_id:
        return HttpResponse("")

    last_local = (
        Local.objects
        .filter(district_id=district_id)
        .exclude(lcode__isnull=True)
        .exclude(lcode__exact="")
        .order_by("-lcode")
        .first()
    )

    if last_local:
        last_code = last_local.lcode
        length = len(last_code)
        next_code = str(int(last_code) + 1).zfill(length)
    else:
        next_code = "00001"

    return HttpResponse(next_code)

@login_required
def local_create(request):
    initial = {}

    district_code = request.GET.get("district")
    if district_code:
        try:
            initial["district"] = District.objects.get(dcode=district_code)
        except District.DoesNotExist:
            pass

    if request.method == "POST":
        form = LocalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Local added successfully.")
            return redirect("properties:local_list")
    else:
        form = LocalForm(initial=initial)

    return render(
        request,
        "properties/local_form.html",
        {
            "form": form,
            "title": "Add Local",
        }
    )

