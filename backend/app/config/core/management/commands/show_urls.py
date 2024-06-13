from django.core.management.base import BaseCommand
from django.urls import get_resolver


class Command(BaseCommand):
    help = "Display all registered URLs"

    def handle(self, *args, **options):
        resolver = get_resolver()
        for pattern in resolver.url_patterns:
            self.print_pattern(pattern)

    def print_pattern(self, pattern, prefix=""):
        if hasattr(pattern, 'url_patterns'):
            for sub_pattern in pattern.url_patterns:
                self.print_pattern(sub_pattern, prefix + pattern.pattern.regex.pattern)
        else:
            self.stdout.write(prefix + pattern.pattern.regex.pattern)
