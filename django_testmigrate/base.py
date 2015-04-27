# -*- coding: utf-8 -*-
# Copyright (C) 2015 via680
#
# Licensed under a BSD 3-Clause License. See LICENSE file.
from __future__ import unicode_literals

from collections import OrderedDict

from django.core.management.commands import migrate
from django.db import models
from django.test import SimpleTestCase


class StateScope(object):
    pass


class MigrateTestCase(SimpleTestCase):
    test = lambda self: None

    _current_state = None

    def __init__(self, *args, **kwargs):
        self._store = OrderedDict()
        self.set_current_state(None)

        super(MigrateTestCase, self).__init__(*args, **kwargs)

    def set_current_state(self, state):
        self._current_state = state

        if state not in self._store:
            self._store[state] = StateScope()

    def __setattr__(self, name, value):
        if isinstance(value, models.Model):
            setattr(self._store[self._current_state], name, value)
        else:
            super(MigrateTestCase, self).__setattr__(name, value)

    def __getattr__(self, name):
        e = None

        for state, scope in reversed(list(self._store.items())):
            try:
                val = getattr(scope, name)
            except AttributeError as ex:
                # needed for Python 3 compatibility
                e = ex
                continue
            else:
                e = None

                # get fresh instance
                if state != self._current_state and \
                        isinstance(val, models.Model):
                    model_meta = val.__class__._meta
                    model_class = self._current_state.get_model(
                        model_meta.app_label,
                        model_meta.model_name
                    )
                    val = model_class.objects.get(pk=val.pk)

                # add this value to the current scope
                setattr(self, name, val)
                break

        if e:
            raise AttributeError("'%s' object has no attribute '%s'" % (
                self.__class__.__name__, name
            ))

        return val


class TestMigrationExecutor(migrate.MigrationExecutor):
    def run_test_func(self, action, *args):
        command = TestMigrationExecutor.command

        state, migration = args

        test_func_name = 'test_%s' % action

        forwards = action.startswith('apply')

        test_func = getattr(migration, test_func_name, None)

        if not test_func:
            return

        if command.verbosity > 0:
            whitespace = '' if forwards else '  '
            command.stdout.write('   %sRunning %s.%s.%s...' % (
                whitespace,
                migration.app_label,
                migration.name,
                test_func_name
            ), command.style.MIGRATE_SUCCESS, ending='')

        rendered_state = state.apps

        command.testcase.set_current_state(rendered_state)

        test_func(rendered_state, command.testcase)

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
