# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.db import connections, DEFAULT_DB_ALIAS, migrations
from django.test.runner import DiscoverRunner

from ...base import TestMigrateCommand, TestMigrationExecutor


option_list = [
    (('--db-name-suffix',), {'action': 'store',
        'dest': 'db_name_suffix', 'default': '',
        'help': 'String appended to the test database name.'}),
    (('--database',), {'action': 'store',
        'dest': 'database', 'default': DEFAULT_DB_ALIAS,
        'help': 'Nominates a database to synchronize. Defaults to the '
        '"default" database.'}),
    (('--no-reverse',), {'action': 'store_true',
        'dest': 'no_reverse', 'default': False,
        'help': 'Migrate backwards after migrating forwards.'}),
]


class Command(BaseCommand):
    can_import_settings = True

    def add_arguments(self, parser):
        [
            parser.add_argument(*args, **kwargs)
            for args, kwargs in option_list
        ]

    def handle(self, *args, **options):
        self.verbosity = int(options.get('verbosity', 1))
        self.no_reverse = options.get('no_reverse')
        self.db_name_suffix = options.get('db_name_suffix')

        # need this available later
        Command.verbosity = self.verbosity

        from django.core.management.commands import migrate
        old_Command = migrate.Command
        migrate.Command = TestMigrateCommand

        runner = DiscoverRunner(verbosity=self.verbosity)
        runner.setup_test_environment()

        # this will do our forwards migrations
        try:
            if self.verbosity > 0:
                self.stdout.write('Running all forwards migrations.',
                    self.style.WARNING)

            old_config = runner.setup_databases(
                db_name_suffix=self.db_name_suffix
            )

            # unless the user asked us not to, migrate backwards.
            if not self.no_reverse:
                db = options.get('database')
                connection = connections[db]

                executor = TestMigrationExecutor(connection)
                # we filter out contenttypes because it causes errors when
                # migrated all the way back.
                root_nodes = [
                    node
                    for node in executor.loader.graph.root_nodes()
                    if node[0] != 'contenttypes'
                ]

                for app_label, migration_name in root_nodes:
                    if self.verbosity > 0:
                        self.stdout.write('Running reverse migrations for %s.'
                            % app_label, self.style.WARNING)
                    try:
                        TestMigrateCommand().execute(
                            app_label,
                            migration_name,
                            app_label=app_label,
                            migration_name=migration_name,
                            verbosity=self.verbosity,
                            interactive=False,
                            database=connection.alias,
                            test_database=True,
                            test_flush=True,
                        )
                    except migrations.Migration.IrreversibleError as e:
                        if self.verbosity > 0:
                            self.stdout.write('\n  Warning in %s.%s: %s' %
                                (app_label, migration_name, e),
                                self.style.WARNING)
        except:
            raise
        else:
            # this doesn't go in the finally block since we might want to
            # inspect the DB after a failure.
            runner.teardown_databases(old_config)
        finally:
            migrate.Command = old_Command
            runner.teardown_test_environment()
