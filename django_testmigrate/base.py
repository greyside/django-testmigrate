# -*- coding: utf-8 -*-
# Copyright (C) 2015 via680
#
# Licensed under a BSD 3-Clause License. See LICENSE file.
from __future__ import unicode_literals

from django.conf import settings
from django.core.management.commands import migrate
from django.test import SimpleTestCase
from django.test.runner import dependency_ordered, DiscoverRunner

class MigrateTestCase(SimpleTestCase):
    test = lambda self: None


class TestMigrationExecutor(migrate.MigrationExecutor):
    def __init__(self, connection, progress_callback=None):
        self._progress_callback = progress_callback
        super(TestMigrationExecutor, self).__init__(connection, progress_callback=self.progress_callback)
    
    def progress_callback(self, action, migration, *args, **kwargs):
        if self._progress_callback:
            kwargs['executor'] = self
            self._progress_callback(action, migration, *args, **kwargs)


class TestMigrateCommand(migrate.Command):
    def run_test_func(self, action, migration, executor, test_func, test_func_name):
        if self.verbosity > 0:
            whitespace = '' if action.startswith('apply') else '  '
            self.stdout.write('   %sRunning %s.%s.%s...' % (whitespace, migration.app_label, migration.name, test_func_name,), self.style.MIGRATE_SUCCESS, ending='')
        
        project_state = executor.loader.project_state((migration.app_label, migration.name), at_end=False)
        
        test_func(project_state.render(), self.testcase)
        
        if self.verbosity > 0:
            self.stdout.write(' OK', self.style.MIGRATE_SUCCESS)
        
    
    def migration_progress_callback(self, action, migration, *args, **kwargs):
        executor = kwargs.pop('executor')
        
        test_func_name = 'test_%s' % action
        
        test_func = getattr(migration, test_func_name, None)
        
        if test_func and action.endswith('start'):
            self.run_test_func(action, migration, executor, test_func, test_func_name)
        
        super(TestMigrateCommand, self).migration_progress_callback(action, migration, *args, **kwargs)
        
        if test_func and action.endswith('success'):
            self.run_test_func(action, migration, executor, test_func, test_func_name)
    
    def handle(self, *args, **kwargs):
        
        self.testcase = MigrateTestCase('test')
        
        old = migrate.MigrationExecutor
        migrate.MigrationExecutor = TestMigrationExecutor
        
        super(TestMigrateCommand, self).handle(*args, **kwargs)
        
        migrate.MigrationExecutor = old


class TestMigrationRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        return setup_databases(self.verbosity, self.interactive, **kwargs)


# the following code mostly copy+pasted from Django, used under a BSD license.


def create_test_db(self, verbosity=1, autoclobber=False, serialize=True, db_name_suffix=None):
    """
    Creates a test database, prompting the user for confirmation if the
    database already exists. Returns the name of the test database created.
    """
    # Don't import django.core.management if it isn't needed.
    from django.core.management import call_command

    test_database_name = self._get_test_db_name()
    
    if db_name_suffix:
        test_database_name += db_name_suffix

    if verbosity >= 1:
        test_db_repr = ''
        if verbosity >= 2:
            test_db_repr = " ('%s')" % test_database_name
        print("Creating test database for alias '%s'%s..." % (
            self.connection.alias, test_db_repr))

    self._create_test_db(verbosity, autoclobber)

    self.connection.close()
    settings.DATABASES[self.connection.alias]["NAME"] = test_database_name
    self.connection.settings_dict["NAME"] = test_database_name

    TestMigrateCommand().execute(
        verbosity=verbosity,
        interactive=False,
        database=self.connection.alias,
        test_database=True,
        test_flush=True,
    )

    # We then serialize the current state of the database into a string
    # and store it on the connection. This slightly horrific process is so people
    # who are testing on databases without transactions or who are using
    # a TransactionTestCase still get a clean database on every test run.
    if serialize:
        self.connection._test_serialized_contents = self.serialize_db_to_string()

    call_command('createcachetable', database=self.connection.alias)

    # Ensure a connection for the side effect of initializing the test database.
    self.connection.ensure_connection()

    return test_database_name


def setup_databases(verbosity, interactive, **kwargs):
    from django.db import connections, DEFAULT_DB_ALIAS

    # First pass -- work out which databases actually need to be created,
    # and which ones are test mirrors or duplicate entries in DATABASES
    mirrored_aliases = {}
    test_databases = {}
    dependencies = {}
    default_sig = connections[DEFAULT_DB_ALIAS].creation.test_db_signature()
    for alias in connections:
        connection = connections[alias]
        test_settings = connection.settings_dict['TEST']
        if test_settings['MIRROR']:
            # If the database is marked as a test mirror, save
            # the alias.
            mirrored_aliases[alias] = test_settings['MIRROR']
        else:
            # Store a tuple with DB parameters that uniquely identify it.
            # If we have two aliases with the same values for that tuple,
            # we only need to create the test database once.
            item = test_databases.setdefault(
                connection.creation.test_db_signature(),
                (connection.settings_dict['NAME'], set())
            )
            item[1].add(alias)

            if 'DEPENDENCIES' in test_settings:
                dependencies[alias] = test_settings['DEPENDENCIES']
            else:
                if alias != DEFAULT_DB_ALIAS and connection.creation.test_db_signature() != default_sig:
                    dependencies[alias] = test_settings.get('DEPENDENCIES', [DEFAULT_DB_ALIAS])

    # Second pass -- actually create the databases.
    old_names = []
    mirrors = []

    for signature, (db_name, aliases) in dependency_ordered(
            test_databases.items(), dependencies):
        test_db_name = None
        # Actually create the database for the first connection
        for alias in aliases:
            connection = connections[alias]
            if test_db_name is None:
                test_db_name = create_test_db(connection.creation,
                    verbosity,
                    autoclobber=not interactive,
                    serialize=connection.settings_dict.get("TEST", {}).get("SERIALIZE", True),
                    db_name_suffix=kwargs.get('db_name_suffix'),
                )
                destroy = True
            else:
                connection.settings_dict['NAME'] = test_db_name
                destroy = False
            old_names.append((connection, db_name, destroy))

    for alias, mirror_alias in mirrored_aliases.items():
        mirrors.append((alias, connections[alias].settings_dict['NAME']))
        connections[alias].settings_dict['NAME'] = (
            connections[mirror_alias].settings_dict['NAME'])

    return old_names, mirrors

