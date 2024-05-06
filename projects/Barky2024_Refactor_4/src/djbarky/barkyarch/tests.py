import os
import django
from django.conf import settings

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'djbarky.settings'

# Configure Django settings
settings.configure(DEBUG=True)  # Add other settings as needed

# Initialize Django application registry
django.setup()

from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import localtime
import datetime as date
from barkyapi.models import Bookmark
from barkyarch.domain.model import DomainBookmark
from barkyarch.services.commands import (
    AddBookmarkCommand,
    GetBookmarkCommand,
    ListBookmarksCommand,
    DeleteBookmarkCommand,
    EditBookmarkCommand,
)


class TestCommands(TestCase):
    def setUp(self):
        right_now = localtime().date()

        self.domain_bookmark_1 = DomainBookmark(
            id=1,
            title="Test Bookmark",
            url="http://www.example.com",
            notes="Test notes",
            date_added=right_now,
        )

        self.domain_bookmark_2 = DomainBookmark(
            id=2,
            title="Test Bookmark 2",
            url="http://www.example2.com",
            notes="Test notes 2",
            date_added=right_now,
        )

    def test_command_add(self):
        add_command = AddBookmarkCommand()
        add_command.execute(self.domain_bookmark_1)

        # run checks
        # one object is inserted
        self.assertEqual(Bookmark.objects.count(), 1)

        # that object is the same as the one we inserted
        self.assertEqual(Bookmark.objects.get(id=1).url, self.domain_bookmark_1.url)

    def test_command_edit(self):

        add_command = AddBookmarkCommand()
        add_command.execute(self.domain_bookmark_1)

        # using command
        # get_command = GetBookmarkCommand()
        # domain_bookmark_temp = get_command.execute(self.domain_bookmark_1.id)
        # domain_bookmark_temp.title = "Goofy"

        # or just modify
        self.domain_bookmark_1.title = "goofy"

        edit_command = EditBookmarkCommand()
        edit_command.execute(self.domain_bookmark_1)

        # run checks
        # one object is inserted
        self.assertEqual(Bookmark.objects.count(), 1)

        # that object is the same as the one we inserted
        self.assertEqual(Bookmark.objects.get(id=1).title, "goofy")
    
    # Listing Bookmarks (Default-Custom by title) 
    def test_list_bookmarks_order_by_default(self):
        # Instantiate ListBookmarksCommand with default order_by parameter
        list_command = ListBookmarksCommand()

        # Execute the command to list bookmarks
        bookmarks = list_command.execute()

        # Assert that the returned list is ordered by default (date_added)
        self.assertEqual(len(bookmarks), 2)
        self.assertEqual(bookmarks[0].title, "Bookmark 1")
        self.assertEqual(bookmarks[1].title, "Bookmark 2")

    def test_list_bookmarks_order_by_custom(self):
        # Instantiate ListBookmarksCommand with custom order_by parameter
        list_command = ListBookmarksCommand(order_by="title")

        # Execute the command to list bookmarks ordered by title
        bookmarks = list_command.execute()

        # Assert that the returned list is ordered by title
        self.assertEqual(len(bookmarks), 2)
        self.assertEqual(bookmarks[0].title, "Bookmark 1")
        self.assertEqual(bookmarks[1].title, "Bookmark 2")
    
    def test_delete_existing_bookmark(self):
        # Instantiate DeleteBookmarkCommand
        delete_command = DeleteBookmarkCommand()

        # Execute the command to delete the test bookmark
        delete_command.execute(DomainBookmark.from_entity(self.test_bookmark))

        # Assert that the bookmark has been deleted from the database
        with self.assertRaises(Bookmark.DoesNotExist):
            Bookmark.objects.get(id=self.test_bookmark.id)

    def test_delete_non_existing_bookmark(self):
        # Instantiate DeleteBookmarkCommand
        delete_command = DeleteBookmarkCommand()

        # Create a new domain bookmark object (not existing in the database)
        non_existing_bookmark = DomainBookmark(
            id=999,
            title="Non-existing Bookmark",
            url="http://www.nonexisting.com",
            notes="Non-existing notes",
            date_added="4/23/24"        )

        # Execute the command to delete a non-existing bookmark
        delete_command.execute(non_existing_bookmark)

        # Assert that no bookmark has been deleted (should not raise error)
        with self.assertRaises(Bookmark.DoesNotExist):
            Bookmark.objects.get(id=999)  # Confirm that the bookmark with ID=999 doesn't exist
