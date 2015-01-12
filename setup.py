#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import django_testmigrate

EXCLUDE_FROM_PACKAGES = ['test_project*']

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
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
)

