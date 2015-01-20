# -*- coding: utf-8 -*-
# Copyright (C) 2015 via680
#
# Licensed under a BSD 3-Clause License. See LICENSE file.
from __future__ import unicode_literals

from django.conf import settings
from django.core.management.commands import migrate
from django.test import SimpleTestCase


class MigrateTestCase(SimpleTestCase):
    test = lambda self: None


class TestMigrationExecutor(migrate.MigrationExecutor):
    def run_test_func(self, action, *args):
        command = TestMigrationExecutor.command
        
        if len(args) == 1:
            # handle Django 1.7
            migration, state = args[0], None
        elif len(args) == 2:
            # handle Django 1.8
            migration, state = args
        
        test_func_name = 'test_%s' % action
        
        test_func = getattr(migration, test_func_name, None)
        
        if not test_func:
            return
        
        if not state:
            state = self.loader.project_state((migration.app_label, migration.name), at_end=False)
        
        if command.verbosity > 0:
            whitespace = '' if action.startswith('apply') else '  '
            command.stdout.write('   %sRunning %s.%s.%s...' % (whitespace, migration.app_label, migration.name, test_func_name,), command.style.MIGRATE_SUCCESS, ending='')
        
        test_func(state.render(), command.testcase)
        
        if command.verbosity > 0:
            command.stdout.write(' OK', command.style.MIGRATE_SUCCESS)
    
    def apply_migration(self, *args, **kwargs):
        self.run_test_func("apply_start", *args)
        
        super(TestMigrationExecutor, self).apply_migration(*args, **kwargs)
        
        self.run_test_func("apply_success", *args)
    
    def unapply_migration(self, *args, **kwargs):
        self.run_test_func("unapply_start", *args)
        
        super(TestMigrationExecutor, self).unapply_migration(*args, **kwargs)
        
        self.run_test_func("unapply_success", *args)


class TestMigrateCommand(migrate.Command):
    
    def handle(self, *args, **kwargs):
        
        self.testcase = MigrateTestCase('test')
        
        TestMigrationExecutor.command = self
        
        old = migrate.MigrationExecutor
        migrate.MigrationExecutor = TestMigrationExecutor
        
        # Django's test runner code will mess with the verbosity, fix it here.
        from django_testmigrate.management.commands.testmigrate import Command
        kwargs['verbosity'] = Command.verbosity
        
        super(TestMigrateCommand, self).handle(*args, **kwargs)
        
        migrate.MigrationExecutor = old

