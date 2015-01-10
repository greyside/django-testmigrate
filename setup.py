#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import django_testmigrate

package_name = 'django_testmigrate'

setup(name='django-testmigrate',
    version=django_testmigrate.__version__,
    description="Lets you write test functions for your migrations.",
    author='Seán Hayes',
    author_email='sean@seanhayes.name',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords='django testmigrate migrations',
    url='https://github.com/greyside/django-testmigrate',
    download_url='https://github.com/greyside/django-testmigrate',
    license='BSD',
    install_requires=[
        'django>=1.7',
        'six',
    ],
    packages=[
        package_name,
        '%s.management.commands' % package_name,
    ],
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
)

