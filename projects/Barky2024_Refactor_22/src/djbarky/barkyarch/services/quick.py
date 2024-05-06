import os
import sys
from pathlib import Path

loc = Path(__file__).parent.parent.parent / "djbarky"

print(f"loc: {loc}")

sys.path.append(os.path.join(os.path.dirname(__file__), f"{loc}"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djbarky.settings")

import django
from django.apps import apps
from django.conf import settings
from django.apps import AppConfig


# if not apps.ready and not settings.configured:
#     django.setup()

django.setup()

settings_list = dir(settings)
print(str(settings_list))

# it is imperative that we test that apps are ready before we can access the models
if apps.ready:
    print("Apps are ready")
    print(str(apps.get_app_configs()))
    bm = apps.get_model("barkyapi", "Bookmark")

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
    print("Bookmarks: ", bm.objects.all())

    # get rid of tests
    bm.objects.all().delete()
