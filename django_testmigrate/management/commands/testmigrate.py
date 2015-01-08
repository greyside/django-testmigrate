from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

from ...base import TestMigrationRunner


class Command(NoArgsCommand):
    can_import_settings = True
    
    def handle_noargs(self, **options):
        self.verbosity = int(options.get('verbosity', 1))
        
        runner = TestMigrationRunner(verbosity=self.verbosity)
        runner.setup_test_environment()
        old_config = runner.setup_databases()
        
        runner.teardown_databases(old_config)
        runner.teardown_test_environment()

