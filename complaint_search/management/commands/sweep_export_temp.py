from django.core.management.base import BaseCommand

from complaint_search.export_temp import (
    get_export_temp_max_age_seconds,
    sweep_export_temp_files,
)


class Command(BaseCommand):
    help = (
        "Remove abandoned complaint export temp directories older than "
        "EXPORT_TEMP_MAX_AGE_SECONDS (default: 1 hour). Schedule hourly via "
        "cron. Increase the setting when very large exports need more time to "
        "build or download; decrease it to reclaim disk sooner."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-age-seconds",
            type=int,
            default=None,
            help=(
                "Override EXPORT_TEMP_MAX_AGE_SECONDS for this run only."
            ),
        )

    def handle(self, *args, **options):
        max_age_seconds = options["max_age_seconds"]
        if max_age_seconds is None:
            max_age_seconds = get_export_temp_max_age_seconds()

        removed = sweep_export_temp_files(max_age_seconds=max_age_seconds)
        self.stdout.write(
            self.style.SUCCESS(
                "Removed {count} export temp director{suffix} older than "
                "{max_age} seconds.".format(
                    count=removed,
                    suffix="y" if removed == 1 else "ies",
                    max_age=max_age_seconds,
                )
            )
        )
