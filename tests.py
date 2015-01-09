from __future__ import print_function

from unittest import TestCase
import subprocess


class SuccessfulMigrationTestCase(TestCase):
    executable = 'coverage run --source=django_testmigrate'
    
    def test(self):
        process = subprocess.Popen(
            self.executable+' manage.py testmigrate --settings=test_project.success_settings',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        print(stdout, stderr)
        
        self.assertEqual(process.returncode, 0)
        self.assertNotEqual(stdout, b'')
        self.assertEqual(stderr, b'')

class FailingMigrationTestCase(TestCase):
    executable = 'coverage run --source=django_testmigrate'
    
    def test(self):
        process = subprocess.Popen(
            self.executable+' manage.py testmigrate --settings=test_project.failure_settings',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        print(stdout, stderr)
        
        self.assertEqual(process.returncode, 1)
        self.assertNotEqual(stdout, b'')
        self.assertNotEqual(stderr, b'')

