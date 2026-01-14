
from django import forms
from .models import Property, HousingUnit, PropertyInventory, ItemTransfer, District, Local, DistrictProperty, DistrictInventory, LocalProperty, LocalInventory, UserProfile, BackupCode, ImportedFile

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = '__all__'

class HousingUnitForm(forms.ModelForm):
    class Meta:
        model = HousingUnit
        fields = '__all__'

class PropertyInventoryForm(forms.ModelForm):
    class Meta:
        model = PropertyInventory
        fields = '__all__'

class ItemTransferForm(forms.ModelForm):
    class Meta:
        model = ItemTransfer
        fields = '__all__'

class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = '__all__'

class LocalForm(forms.ModelForm):
    class Meta:
        model = Local
        fields = '__all__'

class DistrictPropertyForm(forms.ModelForm):
    class Meta:
        model = DistrictProperty
        fields = '__all__'

class DistrictInventoryForm(forms.ModelForm):
    class Meta:
        model = DistrictInventory
        fields = '__all__'

class LocalPropertyForm(forms.ModelForm):
    class Meta:
        model = LocalProperty
        fields = '__all__'

class LocalInventoryForm(forms.ModelForm):
    class Meta:
        model = LocalInventory
        fields = '__all__'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'

class BackupCodeForm(forms.ModelForm):
    class Meta:
        model = BackupCode
        fields = '__all__'

class ImportedFileForm(forms.ModelForm):
    class Meta:
        model = ImportedFile
        fields = '__all__'

from django import forms
from .models import District, Local


from django import forms
from .models import District


from django import forms
from .models import District


class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = ["dcode", "name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default DCODE when ADDING (not editing)
        if not self.instance.pk:
            last_district = (
                District.objects
                .exclude(dcode__isnull=True)
                .exclude(dcode__exact="")
                .order_by("-dcode")
                .first()
            )

            if last_district:
                last_code = last_district.dcode
                length = len(last_code)
                try:
                    next_code = str(int(last_code) + 1).zfill(length)
                except ValueError:
                    next_code = "00001"
            else:
                next_code = "00001"

            self.fields["dcode"].initial = next_code

    # 🔐 UNIQUE DCODE CHECK
    def clean_dcode(self):
        dcode = self.cleaned_data.get("dcode")

        if District.objects.exclude(pk=self.instance.pk).filter(dcode=dcode).exists():
            raise forms.ValidationError(
                "District code already exists. Please use a unique code."
            )

        return dcode

    # 🔐 UNIQUE NAME CHECK
    def clean_name(self):
        name = self.cleaned_data.get("name")

        if District.objects.exclude(pk=self.instance.pk).filter(name__iexact=name).exists():
            raise forms.ValidationError(
                "District name already exists. Please use a unique name."
            )

        return name



from django import forms
from django.urls import reverse
from .models import Local


class LocalForm(forms.ModelForm):
    class Meta:
        model = Local
        fields = ["district", "lcode", "name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --------------------------------------------------
        # Widget styling + HTMX (NO template filters needed)
        # --------------------------------------------------
        self.fields["district"].widget.attrs.update({
            "class": "form-control",
            "hx-get": reverse("properties:next_lcode"),
            "hx-trigger": "change",
            "hx-target": "#id_lcode",
        })

        self.fields["lcode"].widget.attrs.update({
            "class": "form-control",
        })

        self.fields["name"].widget.attrs.update({
            "class": "form-control",
        })

        # --------------------------------------------------
        # Disable LCODE until District is selected (ADD only)
        # --------------------------------------------------
        if not self.instance.pk and not self.data.get("district"):
            self.fields["lcode"].disabled = True

        # --------------------------------------------------
        # Default LCODE per District (ADD only)
        # --------------------------------------------------
        if not self.instance.pk:
         district = (
            self.data.get("district")
            or getattr(self.initial.get("district"), "pk", None)
        )

         if district:
            last_local = (
            Local.objects
            .filter(district_id=district)
            .exclude(lcode__isnull=True)
            .exclude(lcode__exact="")
            .exclude(lcode="777")  # IGNORE Distrito
            .order_by("-lcode")
            .first()
        )

        if last_local:
            last_code = last_local.lcode
            next_code = str(int(last_code) + 1).zfill(3)
        else:
            next_code = "00001"

        self.fields["lcode"].initial = next_code


    # --------------------------------------------------
    # Validation: unique LCODE + NAME within District
    # -------------------------------- ------------------
    def clean(self):
        cleaned_data = super().clean()

        district = cleaned_data.get("district")
        lcode = cleaned_data.get("lcode")
        name = cleaned_data.get("name")

        if not district or not lcode or not name:
            return cleaned_data

        qs = Local.objects.exclude(pk=self.instance.pk).filter(
            district=district
        )

        if qs.filter(lcode=lcode).exists():
            raise forms.ValidationError(
                "This Local Code already exists in the selected District."
            )

        if qs.filter(name__iexact=name).exists():
            raise forms.ValidationError(
                "This Local name already exists in the selected District."
            )

        return cleaned_data
