# national/admin.py
from django.contrib import admin
from .models import (
    District, Local, Report,
    Chapel, PastoralHouse, OfficeBuilding, OtherBuilding, Page1Summary,
    Item, ItemsSummary,
    ItemAdded, ItemAddedSummary,
    ItemRemoved, ItemRemovedSummary,
    Land, LandSummary, Plant, PlantSummary, Vehicle, VehicleSummary,
    ReportSummary
)

admin.site.register(District)
admin.site.register(Local)
admin.site.register(Report)

# Page 1
admin.site.register(Chapel)
admin.site.register(PastoralHouse)
admin.site.register(OfficeBuilding)
admin.site.register(OtherBuilding)
admin.site.register(Page1Summary)

# Page 2
admin.site.register(Item)
admin.site.register(ItemsSummary)

# Page 3
admin.site.register(ItemAdded)
admin.site.register(ItemAddedSummary)

# Page 4
admin.site.register(ItemRemoved)
admin.site.register(ItemRemovedSummary)

# Page 5
admin.site.register(Land)
admin.site.register(LandSummary)
admin.site.register(Plant)
admin.site.register(PlantSummary)
admin.site.register(Vehicle)
admin.site.register(VehicleSummary)

# Report summary
admin.site.register(ReportSummary)
