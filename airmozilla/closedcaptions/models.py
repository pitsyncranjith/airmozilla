import hashlib

from django.contrib.auth.models import User
from django.db import models

from jsonfield import JSONField

from airmozilla.main.models import Event, upload_path_tagged


def _upload_path_closed_captions(instance, filename):
    return upload_path_tagged('closed_captions', instance, filename)


class ClosedCaptions(models.Model):
    event = models.ForeignKey(Event)
    file = models.FileField(upload_to=_upload_path_closed_captions)

    transcript = JSONField(null=True)
    submission_info = JSONField(null=True)
    file_info = JSONField(null=True)

    created_user = models.ForeignKey(
        User,
        related_name='created_user',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def filename_hash(self):
        """this is useful so that we can generate public URLs that
        we can send to services like Vid.yl without needing
        authentication."""
        return hashlib.md5(self.file.name).hexdigest()[:12]
