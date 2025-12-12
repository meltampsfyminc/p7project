from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.management import call_command
import tempfile, os

from .models import District, Local, Report


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
