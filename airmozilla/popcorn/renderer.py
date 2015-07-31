import os
import tempfile
import time
from uuid import uuid4

import boto
from boto.s3.key import Key
from funfactory.urlresolvers import reverse
from popcoder.popcoder import process_json

from django.db import transaction
from django.conf import settings
from django.utils import timezone

from airmozilla.base.utils import build_absolute_url, prepare_vidly_video_url
from airmozilla.popcorn.models import PopcornEdit
from airmozilla.main.models import Event, VidlySubmission
from airmozilla.manage import vidly
from airmozilla.uploads.models import Upload


@transaction.atomic
def render_edit(edit_id):
    edit = PopcornEdit.objects.get(id=edit_id)
    event = edit.event

    filename = '%s.webm' % edit.id
    filepath = os.path.join(tempfile.gettempdir(), filename)
    if not (os.path.isfile(filepath) and
            os.stat(filepath)[os.stat.st_size] > 0):
        edit.status = PopcornEdit.STATUS_PROCESSING
        edit.save()
        process_json(edit.data, out=filepath)

    upload_file_name = '%s.webm' % uuid4().hex[:13]
    # Uploads file to s3
    connection = boto.connect_s3(
        settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY,
    )

    nonexistent = connection.lookup(settings.S3_UPLOAD_BUCKET)
    if nonexistent:
        bucket = connection.create_bucket(settings.S3_UPLOAD_BUCKET)
    else:
        bucket = connection.get_bucket(settings.S3_UPLOAD_BUCKET)

    video_key = Key(bucket)

    video_key.key = upload_file_name
    start = time.time()
    video_key.set_contents_from_filename(filepath)
    end = time.time()

    video_url = video_key.generate_url(expires_in=0, query_auth=False)
    video_url = prepare_vidly_video_url(video_url)

    filesize = os.stat(filepath).st_size

    Upload.objects.create(
        user=edit.user,
        url=video_url,
        file_name=upload_file_name,
        mime_type='video/webm',
        size=filesize,
        upload_time=int(end - start)
    )

    webhook_url = build_absolute_url(reverse('popcorn:vidly_webhook'))
    token_protection = event.privacy != Event.PRIVACY_PUBLIC

    tag, error = vidly.add_media(
        url=video_url,
        token_protection=token_protection,
        hd=True,
        notify_url=webhook_url,
    )

    VidlySubmission.objects.create(
        event=event,
        url=video_url,
        tag=tag,
        hd=True,
        submission_error=error
    )

    # raise exception if error
    if error:
        raise Exception(error)

    edit.status = PopcornEdit.STATUS_SUCCESS
    edit.finished = timezone.now()
    edit.save()

    os.remove(filepath)


def render_all_videos(verbose=False):
    # Re process if start time is more than 2 hours
    pending_edits = PopcornEdit.objects.filter(PopcornEdit.STATUS_PENDING)
    if pending_edits.count() > 1:
        if verbose:
            print "Currently more than one edit. Skipping for now"
            print pending_edits.count()
    pending_edits = pending_edits[:1]
    for pending_edit in pending_edits:
        render_edit(pending_edit.id)
