# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, DEFAULT_DB_ALIAS, migrations

from ...base import TestMigrationRunner, TestMigrateCommand, TestMigrationExecutor


class Command(BaseCommand):
    can_import_settings = True
    
    option_list = BaseCommand.option_list + (
        make_option('--db-name-suffix', action='store', dest='db_name_suffix',
            default='', help='String appended to the test database name.'),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to synchronize. '
                'Defaults to the "default" database.'),
        make_option('--no-reverse', action='store_true', dest='no_reverse',
            default=False, help='Migrate backwards after migrating forwards.'),
    )
    
    def handle(self, *args, **options):
        self.verbosity = int(options.get('verbosity', 1))
        self.no_reverse = options.get('no_reverse')
        self.db_name_suffix = options.get('db_name_suffix')
        
        runner = TestMigrationRunner(verbosity=self.verbosity)
        runner.setup_test_environment()
        
        # this will do our forwards migrations
        try:
            old_config = runner.setup_databases(db_name_suffix=self.db_name_suffix)
        except:
            raise
        else:
            # this doesn't go in the finally block since we might want to inspect
            # the DB after a failure.
            runner.teardown_databases(old_config)
            
            # unless the user asked us not to, migrate backwards.
            if not self.no_reverse:
                db = options.get('database')
                connection = connections[db]
                
                executor = TestMigrationExecutor(connection)
                root_nodes = executor.loader.graph.root_nodes()
                
                for app_name, migration_name in root_nodes:
                    try:
                        TestMigrateCommand().execute(
                            app_name,
                            migration_name,
                            verbosity=self.verbosity,
                            interactive=False,
                            database=connection.alias,
                            test_database=True,
                            test_flush=True,
                        )
                    except migrations.Migration.IrreversibleError as e:
                        if self.verbosity > 0:
                            self.stdout.write('\n  Warning in %s.%s: %s' % (app_name, migration_name, e), self.style.WARNING)
        finally:
            runner.teardown_test_environment()

