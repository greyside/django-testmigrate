from __future__ import print_function

from unittest import TestCase
import subprocess


class MigrationTestCase(TestCase):
    executable = 'coverage run -a --source=django_testmigrate,test_project/test_success/migrations,test_project/test_failure/migrations'
    cmd = executable+" manage.py testmigrate -v 2 --settings=test_project.%s_settings"
    
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

