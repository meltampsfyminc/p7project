from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.management import call_command
import tempfile, os

from .models import District, Local, Report
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import (
    District, Local, Report,
    Chapel, PastoralHouse, OfficeBuilding, OtherBuilding,
    Item, ItemsSummary,
    ItemAdded, ItemAddedSummary,
    ItemRemoved, ItemRemovedSummary,
    Land, LandSummary,
    Plant, PlantSummary,
    Vehicle, VehicleSummary,
    ReportSummary
)

from national.management.commands.utils_export import render_to_pdf, render_to_docx

@login_required
def district_list(request):
    districts = District.objects.all().order_by("dcode")
    return render(request, "national/district_list.html", {"districts": districts})


@login_required
def local_list(request, dcode):
    district = get_object_or_404(District, dcode=dcode)
    locals = district.locals.all().order_by("lcode")
    return render(request, "national/local_list.html", {"district": district, "locals": locals})


@login_required
def report_list(request, local_id):
    local = get_object_or_404(Local, id=local_id)
    reports = local.reports.all().order_by("-year")
    return render(request, "national/report_list.html", {"local": local, "reports": reports})




def report_print_pdf(request, report_id):
    """Generate PDF or DOCX output for a complete National report."""

    report = get_object_or_404(Report, id=report_id)
    local = report.local
    district = local.district

    # ----------------------------
    # PAGE 1 — Buildings
    # ----------------------------
    chapels = Chapel.objects.filter(report=report)
    pastoral = PastoralHouse.objects.filter(report=report)
    offices = OfficeBuilding.objects.filter(report=report)
    other_buildings = OtherBuilding.objects.filter(report=report)

    page1_summary = getattr(report, "page1_summary", None)

    # ----------------------------
    # PAGE 2 — Items
    # ----------------------------
    items = Item.objects.filter(report=report)
    items_summary = getattr(report, "items_summary", None)

    # ----------------------------
    # PAGE 3 — Items Added
    # ----------------------------
    added_items = ItemAdded.objects.filter(report=report)
    added_summary = getattr(report, "items_added_summary", None)

    # ----------------------------
    # PAGE 4 — Items Removed
    # ----------------------------
    removed_items = ItemRemoved.objects.filter(report=report)
    removed_summary = getattr(report, "items_removed_summary", None)

    # ----------------------------
    # PAGE 5 — Land / Plants / Vehicles
    # ----------------------------
    lands = Land.objects.filter(report=report)
    land_summary = getattr(report, "land_summary", None)

    plants = Plant.objects.filter(report=report)
    plant_summary = getattr(report, "plant_summary", None)

    vehicles = Vehicle.objects.filter(report=report)
    vehicle_summary = getattr(report, "vehicle_summary", None)

    # Entire summary (P1–P5 totals)
    full_summary = getattr(report, "summary", None)

    # ----------------------------
    # Build context for template
    # ----------------------------
    context = {
        "report": report,
        "local": local,
        "district": district,

        # Page 1
        "chapels": chapels,
        "pastoral": pastoral,
        "offices": offices,
        "other_buildings": other_buildings,
        "page1_summary": page1_summary,

        # Page 2
        "items": items,
        "items_summary": items_summary,

        # Page 3
        "added_items": added_items,
        "added_summary": added_summary,

        # Page 4
        "removed_items": removed_items,
        "removed_summary": removed_summary,

        # Page 5
        "lands": lands,
        "land_summary": land_summary,
        "plants": plants,
        "plant_summary": plant_summary,
        "vehicles": vehicles,
        "vehicle_summary": vehicle_summary,

        # Aggregate
        "full_summary": full_summary,
    }

    fmt = request.GET.get("format", "pdf").lower()

    # ----------------------------
    # DOCX OUTPUT
    # ----------------------------
    if fmt == "docx":
        docx_bytes = render_to_docx(context)
        filename = f"Report-{district.dcode}-{local.lcode}-{report.year}.docx"
        response = HttpResponse(
            docx_bytes,
            content_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    # ----------------------------
    # PDF OUTPUT (default)
    # ----------------------------
    pdf_bytes = render_to_pdf("national/report_print.html", context)

    if not pdf_bytes:
        return HttpResponse("Failed to generate PDF.", status=500)

    filename = f"Report-{district.dcode}-{local.lcode}-{report.year}.pdf"
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response



@login_required
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return render(request, "national/report_detail.html", {
        "report": report,
        "page1": report.page1.all(),
        "page2": report.page2.all(),
        "page3": report.page3.all(),
        "page4": report.page4.all(),
        "page5": report.page5.all(),
        "summary": getattr(report, "summary", None),
    })

def district_summary(request, dcode):
    district = get_object_or_404(District, dcode=dcode)
    locals = district.locals.all()

    reports = Report.objects.filter(local__in=locals)

    context = {
        "district": district,
        "locals": locals,
        "reports": reports,
    }

    return render(request, "national/district_summary.html", context)
@login_required
def upload_file(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            messages.error(request, "No file selected")
            return redirect("national:upload")

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        for chunk in file.chunks():
            temp.write(chunk)
        temp.close()

        try:
            call_command("import_national", file=temp.name, user=request.user.id)
            messages.success(request, "File imported successfully.")
        except Exception as e:
            messages.error(request, f"Import failed: {e}")
        finally:
            os.unlink(temp.name)

        return redirect("national:district_list")

    return render(request, "national/upload.html")
