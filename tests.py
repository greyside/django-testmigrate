from __future__ import print_function

from collections import OrderedDict
import subprocess
from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock


class MigrationTestCase(TestCase):
    executable = 'coverage run -a --source=django_testmigrate,test_project/test_success/migrations,test_project/test_failure/migrations,test_project/test_success_reverse_halted/migrations'
    cmd = executable+" manage.py testmigrate --settings=test_project.%s_settings"
    
    def test_success_reverse_migrations_complete(self):
        process = subprocess.Popen(
            self.cmd % 'success',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        print('\n', stdout, stderr)
        
        self.assertEqual(process.returncode, 0)
        self.assertNotEqual(stdout, b'')
        self.assertEqual(stderr, b'')
    
    def test_success_reverse_migrations_halted(self):
        process = subprocess.Popen(
            self.cmd % 'success_reverse_halted',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        print('\n', stdout, stderr)
        
        self.assertEqual(process.returncode, 0)
        self.assertNotEqual(stdout, b'')
        self.assertEqual(stderr, b'')
    
    def test_failure(self):
        process = subprocess.Popen(
            self.cmd % 'failure',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        print(stdout, stderr)
        
        self.assertEqual(process.returncode, 1)
        self.assertNotEqual(stdout, b'')
        self.assertNotEqual(stderr, b'')


class MigrateTestCaseTestCase(TestCase):
    def test_scope(self):
        from django.conf import settings
        settings.configure()
        from django.contrib.auth.models import User
        from django_testmigrate.base import MigrateTestCase, StateScope
        
        MockUser = mock.Mock()
        MockUser.objects.get.side_effect = lambda *args, **kwargs: User(*args, **kwargs)
        
        test_case = MigrateTestCase('test')
        
        # try to get variable before there's a scope set.
        with self.assertRaises(AttributeError):
            test_case.baz
        
        self.assertTrue(isinstance(test_case._store, OrderedDict))
        self.assertTrue(isinstance(test_case._store[None], StateScope))
        
        state1 = mock.Mock()
        
        test_case.set_current_state(state1)
        test_case.foo = 'a string'
        state1model1 = test_case.model1 = User(id=1)
        
        self.assertTrue(isinstance(test_case._store[state1], StateScope))
        
        # models get scoped, but other values stored directly on MigrateTestCase
        self.assertIs(test_case.__dict__['foo'], test_case.foo)
        self.assertNotIn('model1', test_case.__dict__)
        self.assertEqual(test_case._store[state1].model1, state1model1)
        self.assertIs(test_case._store[state1].model1, state1model1)
        self.assertIs(test_case.model1, state1model1)
        
        with self.assertRaises(AttributeError):
            test_case.bar
        
        state2 = mock.Mock()
        
        test_case.set_current_state(state2)
        
        state3 = mock.Mock()
        state3.get_model.side_effect = lambda app_label, model_name: MockUser
        
        test_case.set_current_state(state3)
        
        self.assertIs(test_case.__dict__['foo'], test_case.foo)
        
        self.assertEqual(state3.get_model.call_count, 0)
        
        state3model1 = test_case.model1
        
        # models in different scopes should pass the equality test because they
        # share the same pk, but will actually be different objects.
        self.assertEqual(state1model1, state3model1)
        self.assertIsNot(state1model1, state3model1)
        
        self.assertIs(test_case._store[state1].model1, state1model1)
        self.assertIs(test_case._store[state3].model1, state3model1)
        
        self.assertIs(test_case.model1, state3model1)
        
        self.assertEqual(state3.get_model.call_count, 1)
        self.assertEqual(state3.get_model.call_args_list[0][0], (User._meta.app_label, User._meta.model_name))

