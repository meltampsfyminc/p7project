from django.utils import timezone
from django.db import transaction

from admin_core.models import SyncConflict, Worker


class ConflictResolver:

    @staticmethod
    @transaction.atomic
    def accept(conflict, user):
        """
        Replace existing worker data with incoming payload
        """
        worker = conflict.worker
        payload = conflict.incoming_payload

        worker.first_name = payload.get("first_name", worker.first_name)
        worker.middle_name = payload.get("middle_name", worker.middle_name)
        worker.last_name = payload.get("last_name", worker.last_name)
        worker.updated_at = timezone.now()
        worker.save()

        conflict.status = "accepted"
        conflict.resolved_at = timezone.now()
        conflict.resolved_by = user
        conflict.save()

    @staticmethod
    @transaction.atomic
    def merge(conflict, user, merge_map):
        """
        Merge selected fields only
        merge_map example:
        { "first_name": "incoming", "last_name": "existing" }
        """
        worker = conflict.worker

        for field, source in merge_map.items():
            if source == "incoming":
                worker.__dict__[field] = conflict.incoming_payload.get(field)

        worker.updated_at = timezone.now()
        worker.save()

        conflict.status = "merged"
        conflict.resolved_at = timezone.now()
        conflict.resolved_by = user
        conflict.save()

    @staticmethod
    def reject(conflict, user):
        """
        Ignore incoming data
        """
        conflict.status = "rejected"
        conflict.resolved_at = timezone.now()
        conflict.resolved_by = user
        conflict.save()
