import logging
import os
import shutil
import tempfile
import time

from django.conf import settings

from complaint_search.defaults import (
    EXPORT_TEMP_DIR_PREFIX,
    EXPORT_TEMP_MAX_AGE_SECONDS,
)


log = logging.getLogger(__name__)


def get_export_temp_base_dir():
    return getattr(settings, "EXPORT_TEMP_BASE_DIR", tempfile.gettempdir())


def get_export_temp_max_age_seconds():
    return getattr(
        settings, "EXPORT_TEMP_MAX_AGE_SECONDS", EXPORT_TEMP_MAX_AGE_SECONDS
    )


def create_export_temp_dir():
    return tempfile.mkdtemp(
        prefix=EXPORT_TEMP_DIR_PREFIX,
        dir=get_export_temp_base_dir(),
    )


def sweep_export_temp_files(max_age_seconds=None):
    """Remove abandoned export temp directories older than max_age_seconds.

    Schedule via cron (for example hourly):
        python manage.py sweep_export_temp

    Tune EXPORT_TEMP_MAX_AGE_SECONDS in settings when exports are very large:
    the value should exceed both build time and expected download time.
    """
    max_age = (
        max_age_seconds
        if max_age_seconds is not None
        else get_export_temp_max_age_seconds()
    )
    base_dir = get_export_temp_base_dir()
    cutoff = time.time() - max_age
    removed = 0

    try:
        entries = os.listdir(base_dir)
    except OSError:
        log.exception("Unable to list export temp directory %s", base_dir)
        return removed

    for name in entries:
        if not name.startswith(EXPORT_TEMP_DIR_PREFIX):
            continue

        path = os.path.join(base_dir, name)
        if not os.path.isdir(path):
            continue

        try:
            if os.path.getmtime(path) < cutoff:
                shutil.rmtree(path, ignore_errors=True)
                removed += 1
        except OSError:
            log.exception("Failed to sweep export temp directory %s", path)

    return removed
