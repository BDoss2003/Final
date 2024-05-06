from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import localtime

from barkyapi.models import Bookmark
from barkyarch.domain.model import DomainBookmark
from barkyarch.adapters import repository
from barkyarch.services.uow import DjangoUnitOfWork


class RepositoryTests(TestCase):
    def setUp(self):
        rightnow = localtime().date()

        self.repository = repository.DjangoRepository()
        self.domain_bookmark_1 = DomainBookmark(
            id=1,
            title="Awesome Django",
            url="https://awesomedjango.org/",
            notes="Best place on the web for Django.",
            date_added=rightnow,
        )

    def test_repository_add(self):
        self.repository.add(self.domain_bookmark_1)
        self.assertEqual(Bookmark.objects.count(), 1)


class UoWTests(TestCase):
    def setUp(self):
        rightnow = localtime().date()

        self.domain_bookmark_1 = DomainBookmark(
            id=1,
            title="Awesome Django",
            url="https://awesomedjango.org/",
            notes="Best place on the web for Django.",
            date_added=rightnow,
        )

        self.domain_bookmark_2 = DomainBookmark(
            id=1,
            title="Django News",
            url="https://django-news.com/",
            notes="Weekly Django news, articles, projects, and more.",
            date_added=rightnow,
        )

    def test_uow_add_update(self):
        uow = DjangoUnitOfWork()

        with uow:
            print(f"Bookmarks before: {uow.bookmarks.bookmarks_set}")
            uow.bookmarks.add(self.domain_bookmark_1)
            uow.bookmarks.add(self.domain_bookmark_2)
            uow.commit()
            print(f"Bookmarks before: {uow.bookmarks.bookmarks_set}")
            # good ole W3Schools: https://www.w3schools.com/python/gloss_python_set_length.asp
            # this will show that the transaction has committed two records prior to the rollback
            self.assertEqual(len(uow.bookmarks.bookmarks_set), 2)

        # the transaction records will have been rolled back. The count will be 1 from the repo test.
        self.assertEqual(Bookmark.objects.count(), 1)
