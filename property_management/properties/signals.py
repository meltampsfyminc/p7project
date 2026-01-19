from django.db.models.signals import post_save
from django.dispatch import receiver

from admin_core.management.commands.sync_admin_core import run_sync
from properties.models import ImportedFile



@receiver(post_save, sender=ImportedFile)
def trigger_admin_core_sync(sender, instance, created, **kwargs):
    """
    Automatically sync admin_core after a successful inventory import.
    """

    # Only trigger on successful or partial imports
    if instance.status not in ("success", "partial"):
        return

    # Prevent re-trigger loops (important)
    if hasattr(instance, "_sync_triggered"):
        return

    instance._sync_triggered = True

    # Run sync
    run_sync(triggered_by="import_inventory")
