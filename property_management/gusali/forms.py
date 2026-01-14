from django import forms
from .models import Building, BuildingYearlyRecord
from properties.models import District, Local


class BuildingForm(forms.ModelForm):
    # VIRTUAL FIELDS (not in model)
    district = forms.ModelChoiceField(
        queryset=District.objects.all().order_by("name"),
        label="District",
        empty_label="Select District"
    )

    local = forms.ModelChoiceField(
        queryset=Local.objects.none(),
        label="Local Code",
        empty_label="Select Local"
    )

    class Meta:
        model = Building
        # Exclude raw codes – they will be auto-filled
        exclude = ["dcode", "lcode"]
        widgets = {
            "donation_date": forms.DateInput(attrs={"type": "date"}),
            "ownership_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # EDIT MODE: preload district & locals
        if self.instance.pk and self.instance.local:
            district = self.instance.local.district
            self.fields["district"].initial = district
            self.fields["local"].queryset = Local.objects.filter(
                district=district
            ).order_by("name")
            self.fields["local"].initial = self.instance.local

        # POST MODE: filter locals based on selected district
        elif "district" in self.data:
            try:
                district_id = int(self.data.get("district"))
                self.fields["local"].queryset = Local.objects.filter(
                    district_id=district_id
                ).order_by("name")
            except (ValueError, TypeError):
                pass

    def save(self, commit=True):
        instance = super().save(commit=False)

        district = self.cleaned_data["district"]
        local = self.cleaned_data["local"]

        # Auto-populate codes
        instance.dcode = district.dcode
        instance.lcode = local.lcode
        instance.local = local

        if commit:
            instance.save()
        return instance


class BuildingYearlyRecordForm(forms.ModelForm):
    class Meta:
        model = BuildingYearlyRecord
        exclude = ["building"]
