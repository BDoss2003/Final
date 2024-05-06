# useful guide: https://www.pythontutorial.net/python-unit-testing/python-unittest/
# note that Django's TestCase class is a subclass of Python's unittest.TestCase class so tutorials
# on unittest.TestCase are applicable to Django's TestCase class.

# django settings makes this clear: https://docs.djangoproject.com/en/5.0/topics/settings/

import os
import sys
from pathlib import Path
import unittest

from barky.domain.model import Bookmark

loc = Path(__file__).parent.parent.parent / "djbarky"

sys.path.append(os.path.join(os.path.dirname(__file__), f"{loc}"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djbarky.settings")

import django
from django.apps import apps
from django.conf import settings
from django.apps import AppConfig


class TestCaseRepository(unittest.TestCase):
    def tearDown(self) -> None:
        pass

    def setUp(self) -> None:
        # must be run first
        django.setup()

    def test_repository_list(self):
        # from barky.adapters import repository
        # from barky.services.uow import DjangoUnitOfWork, DjangoApiUnitOfWork

        # without a lot of additional scaffolding, it is very very difficult to get
        # the Django ORM to work outside of a Django app. The Django ORM is tightly bound
        # to the Django app and the Django app's settings. This is a major drawback.

        # it is very unlikely that we will remain committed to the repository or unit of work
        # patterns outside of Django.

        # it is imperative that we test that apps are ready before we can access the models
        if apps.ready:
            print("Apps are ready")
            # print(str(apps.get_app_configs()))
            bm = apps.get_model("barkyapi", "Bookmark")

            # get rid of tests
            bm.objects.all().delete()

            # create some test data
            bm.objects.create(
                id=1,
                title="Test Title",
                url="http://test.com",
                notes="Test notes",
                date_added="2021-01-01",
            )
            bm.objects.create(
                id=2,
                title="Test Title 2",
                url="http://test2 .com",
                notes="Test notes 2",
                date_added="2021-01-02",
            )
            # print("Bookmarks: ", bm.objects.all())

            # test that two records were entered
            self.assertEqual(bm.objects.all().count(), 2)

            # test that two records were entered
            self.assertEqual(bm.objects.first().id, 1)

            # get rid of tests
            bm.objects.all().delete()

    def test_repository_create(self):
        pass

    def test_repository_update(self):
        pass

    def test_repository_delete(self):
        pass

    def test_repository_get(self):
        pass
