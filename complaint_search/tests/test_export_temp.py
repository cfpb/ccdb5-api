import os
import time
from unittest import mock

from django.test import TestCase, override_settings

from complaint_search.defaults import EXPORT_TEMP_DIR_PREFIX
from complaint_search.export_temp import (
    create_export_temp_dir,
    sweep_export_temp_files,
)


class ExportTempTest(TestCase):
    def setUp(self):
        self.temp_base = self.enterContext(
            mock.patch(
                "complaint_search.export_temp.get_export_temp_base_dir",
                return_value=self._test_temp_dir(),
            )
        )

    def _test_temp_dir(self):
        import tempfile

        return tempfile.mkdtemp(prefix="ccdb5-export-temp-test-")

    def _create_export_dir(self, name):
        path = os.path.join(self.temp_base, name)
        os.mkdir(path)
        return path

    @override_settings(EXPORT_TEMP_MAX_AGE_SECONDS=3600)
    def test_create_export_temp_dir_uses_prefix(self):
        path = create_export_temp_dir()
        self.addCleanup(lambda: os.path.exists(path) and os.rmdir(path))
        self.assertTrue(os.path.basename(path).startswith(EXPORT_TEMP_DIR_PREFIX))

    @override_settings(EXPORT_TEMP_MAX_AGE_SECONDS=3600)
    def test_sweep_removes_only_old_prefixed_directories(self):
        old_export = self._create_export_dir(
            "{prefix}old".format(prefix=EXPORT_TEMP_DIR_PREFIX)
        )
        new_export = self._create_export_dir(
            "{prefix}new".format(prefix=EXPORT_TEMP_DIR_PREFIX)
        )
        other_dir = self._create_export_dir("other-dir")

        old_time = time.time() - 7200
        os.utime(old_export, (old_time, old_time))

        removed = sweep_export_temp_files()

        self.assertEqual(removed, 1)
        self.assertFalse(os.path.exists(old_export))
        self.assertTrue(os.path.exists(new_export))
        self.assertTrue(os.path.exists(other_dir))

    @override_settings(EXPORT_TEMP_MAX_AGE_SECONDS=1800)
    def test_sweep_honors_max_age_override(self):
        stale_export = self._create_export_dir(
            "{prefix}stale".format(prefix=EXPORT_TEMP_DIR_PREFIX)
        )
        stale_time = time.time() - 2400
        os.utime(stale_export, (stale_time, stale_time))

        removed = sweep_export_temp_files(max_age_seconds=1800)

        self.assertEqual(removed, 1)
        self.assertFalse(os.path.exists(stale_export))
