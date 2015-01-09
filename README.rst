==================
django-testmigrate
==================

.. image:: https://travis-ci.org/greyside/django-testmigrate.svg?branch=master
    :target: https://travis-ci.org/greyside/django-testmigrate
.. image:: https://coveralls.io/repos/greyside/django-testmigrate/badge.png?branch=master
    :target: https://coveralls.io/r/greyside/django-testmigrate?branch=master

Run automated tests for your migrations.

--------------
Add Tests to Your Migrations
--------------

Four optional test method can be added to your migration classes:

* test_apply_start - Run before this migration.
* test_apply_success - Run after this migration.
* test_unapply_start - Run before this migration is reversed.
* test_unapply_success - Run after this migration is reversed.

::

    class Migration(migrations.Migration):

        dependencies = [
            ('myapp', '0001_initial'),
        ]

        operations = [
            migrations.RunPython(
                populate_data,
                populate_data_rev,
            ),
        ]
        
        def test_apply_start(self, apps, testcase):
            """
            self - This migration instance.
            apps - The project_state for this app, same as what's passed in to
                functions for migrations.RunPython.
            testcase - A TestCase instance to provide the assertions you're used to.
                This instance is shared between migration test functions in case you
                need to share state.
            """
            MyModel = apps.get_model("myapp", "MyModel")
            
            testcase.assertEqual(MyModel.objects.count(), 5)
        
        def test_apply_success(self, apps, testcase):
            pass
        
        def test_unapply_start(self, apps, testcase):
            pass
        
        def test_unapply_success(self, apps, testcase):
            pass

--------------
Run Your Tests
--------------

::

    ./manage.py testmigrate



