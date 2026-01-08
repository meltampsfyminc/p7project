
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
