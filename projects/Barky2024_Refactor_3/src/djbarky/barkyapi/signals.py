import csv
from pathlib import Path

from django.core.files import File
from django.db.models.signals import post_save

from .models import Bookmark


# making sense of this example:
# - save_bookmark is the receiver function
# - Bookmark is the sender and post_save is the signal.
# - Use Case: Everytime a Bookmark is saved, the save_profile function will be executed.
def log_bookmark_to_csv(sender, instance, **kwargs):
    print("I am a signal! I was called because a Bookmark was saved!")

    file = Path(__file__).parent.parent / "barkyarch" / "domain" / "created_log.csv"
    print(f"Writing to {file}")

    # the with statement takes advantate of the context manager protocol: https://realpython.com/python-with-statement/#the-with-statement-approach
    # for reference, here is how open() works: https://docs.python.org/3/library/functions.html#open
    with open(file, "a+", newline="") as csvfile:
        logfile = File(csvfile)
        logwriter = csv.writer(
            logfile,
            delimiter=",",
        )
        logwriter.writerow(
            [
                instance.id,
                instance.title,
                instance.url,
                instance.notes,
                instance.date_added,
            ]
        )

# connect the signal to this receiver
post_save.connect(log_bookmark_to_csv, sender=Bookmark)
