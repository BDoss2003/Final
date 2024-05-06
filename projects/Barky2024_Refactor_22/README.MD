# Barky Refactor 22

The major difference in this refactor is the inclusion of a few key concepts which are explored in depth in P&G:

- **Repository**: by abstracting state change operations on the entities within the domain, we can replace/insert any number of data persistence strategies.
  - P&G Readings: Chapters 2-5
- **Unit of Work**: The unit of work is a means of encapsulating and describing transation-like operations with your system such that any number of needed operations can be coordinated and completed that, collectively constitude an whole operation's completion. In effect, this is more-or-less the equivalent of a database transaction.
  - P&G Readings: Chapters 6 and 7.
- Project structure with setuptools
- Use of `unittest` rather than `pytest`.

## Why is there a Refactor 22?

Django is a monolithic architecture whose bootstrap process expects the settings.py module to be read from within the root/base project where all additional apps are listed. Any given app can use other **utility** code, but Django doesn't want other code to call its elements without considerable additional effort to **ignite** Django's own bootstrap process first.

Thus, regardless of whether we place our archiecture completely outside of the Django project (ensuring that PYTHONPATH is set to include that location), or even within the Django project structure, Django expects its own setup routine to be first called, with settings set, before any Django things can happen. This is normal behavior for a [monolithic architecture](https://www.linkedin.com/pulse/understanding-architecture-django-monolithic-approach-amin-zamani/). Whereas in their last chapters, P&G introduce a bootstrap, we do not need a bootstrap as Django handles that.

So, there are probably a few things we'll need to re-examine:

- **Repository** - we can still do this, but it must be tested via one of the Apps you've identified in Django's settings. Whereas I'm sure we can use the repository now to bypass Django's O/RM, it seems mostly wierd to make our respository an app within Django

## New to Refactor 22

In this refactor, we have three main choices to consider if we wan't any Django-adjacent things like the services, domain, and adapters from P&G (Django views are considered endpoints). Don't forget that [Django's MVT](https://www.geeksforgeeks.org/django-project-mvt-structure/) is itself an architectural pattern.

1. _Option 1_ is to leave architecture code outside of Django folder/file structure and considering using setuptools to make it an installable package (which we left behind in refactor 2). This is fine but the actual cross-talk will still require that testing this package happens within Django.
1. _Option 2_ is the place architecture code witin Django's structure, but this does not exonerate us from needing to ensure that Django's bootstrap/setup process still launches. We still can't test from within the module without extra hassle, so this seems like it'll be better than option 1, but that's not really the case either.
1. _Option 3_ is that we make the repository and other architectural code a Django app itself and thus tightly coupling the presumably independent architecture to Django's itself. This option makes testing and cross-communication much easier.

### A fourth way

A fourth way would be to write other code that accesses the endpoints of the DRF services we expose and leave Django to its own devices. We can demonstrate this, but we still would be resigned to just this method as Django's O/RM can't be used outside of Django without running Django. Testing endpoints is fine and this creates a hybrid where Django is still being used more for a micro-services arhictecture rather than the contining monolith. We would not use any of Django's templating or presentation capabilities with this approach.

### We Won't Continue Down this Path

We will not likely put the effort into the CRUD (repository pattern) and transaction (Unit Of Work) facilities of the architectural patterns from chapters 1 to 7 with Django as features or facilities that exist **OUTSIDE** of the Django project framework. This is because we are fundamentally fighting Django to get these done. This is probably why P&G chose Flask/SQLAlchemy as they are more loosely coupled which makes it easier to include them as part of an overall architecture.

However, we can more readily and easily implement these within the Django project structure. While this is indeed feasible, it lessens the impact and advantage of the pattern as we are not truly independent of Django. There are valid workarounds, but they stray back into the territory of fighting the intrinsic design of the Django Framework.

Although potentially very easy to miss, P&G realize that they have to coerce Django to play outside of the Django project structure with their discussion in this part of Appendix D: [API: Django Views Are Adapters](https://www.cosmicpython.com/book/appendix_django.html#_api_django_views_are_adapters):

```python
os.environ["DJANGO_SETTINGS_MODULE"] = "djangoproject.django_project.settings"
django.setup()


@csrf_exempt
def add_batch(request):
    data = json.loads(request.body)
    eta = data["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        data["ref"], data["sku"], data["qty"], eta,
        unit_of_work.DjangoUnitOfWork(),
    )
    return HttpResponse("OK", status=201)


@csrf_exempt
def allocate(request):
    data = json.loads(request.body)
    try:
        batchref = services.allocate(
            data["orderid"],
            data["sku"],
            data["qty"],
            unit_of_work.DjangoUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return JsonResponse({"message": str(e)}, status=400)

    return JsonResponse({"batchref": batchref}, status=201)
```

P&G discuss the ins and outs of Django app architecture and refer to [this post](https://forum.djangoproject.com/t/where-to-put-business-logic-in-django/282/7) on the matter of how to extend/modify Django's out-of-the-box design when/as needed. Of course, the book's [Epilogue](https://www.cosmicpython.com/book/epilogue_1_how_to_get_there_from_here.html) is also a great read on the matter of how to balance and make sense out of the book's material.

## Updated project strcuture

- **djbarky** - the main Django project
- **barkyapi** - the DRF app
- **barkyarch** - the architectural elements that mirror those from P&G

I do not anticipate leaving things this way for refactor 3 and 4 as we might simply let Django be a monolith and operate within Django to capitilize on a hybrid approach between monolithic and microservices.

## Running Tests Outside of Django

The main issue we'll be facing is that when our tests must run outside of Django, they must bootstrap/setup Django first.

[Ben Lopatin](https://www.benlopatin.com/) - [also on Github](https://github.com/bennylope) - has a good resources that summarizes how to test outside of the Django project structure: [Testing outside of a project](https://www.django-standalone-apps.com/part1/testing.html).

Key takeaways can be seen in the following code:

```python
#!/usr/bin/env python

import sys

try:
    import django
    from django.conf import settings

    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            }
        },
        ROOT_URLCONF="tests.urls",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "myapp",
        ],
        SITE_ID=1,
        NOSE_ARGS=['-s'],
        FIXTURE_DIRS=['tests/fixtures']
    )
    django.setup()

    from django_nose import NoseTestSuiteRunner

except ImportError:
    raise ImportError("To fix this error, run: pip install -r requirements.txt")


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    test_runner = NoseTestSuiteRunner(verbosity=1)
    failures = test_runner.run_tests(test_args)
    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
```

Ben goes on to identify that the Django Documentation also has recommendations in this regard:

```python
#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))
```

This is connected to the need to make sure that we configure and setup (bootstrap) Django first before using it in any external code: [Calling django.setup() is required for “standalone” Django usage](https://docs.djangoproject.com/en/5.0/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage).

Ben Lopatin puts the question on whether we want "standalone" independence to serve as the basis of an entire book (which I bought): [Django Standalone Apps: Learn to Develop Reusable Django Libraries. Apress](https://link.springer.com/book/10.1007/978-1-4842-5632-9)

> In defining the scope of a potential Django standalone app, the first questions you need to ask are whether the package you have in mind needs to be a Django app or just a Python package using Django and secondly how Django-specific your package ought to be even if it isn’t an app.

> The first question is a somewhat minor question, but gets at how your app should be integrated into other Django projects and development workflows. It’s easy to see Django imports in your Python files and think “ah, this is an app,” when in fact it’s non-installable library code (non-installable in the sense of your INSTALLED_APPS, not in the sense of an installed package). For example, if you had some additional form fields that you wanted to distribute, these could be distributed and used as a “regular” Python library, without adding the module to your list of INSTALLED_APPS. You’ll still have to consider the issues discussed in subsequent chapters, such as testing, documentation, and packaging, but with minor differences in how you set up your tests and document usage.

> On the other hand, your prospective package may be incredibly useful in Django projects but have no hard requirements on Django, being agnostic to web framework or even to being used for web applications at all. If this is the case, then you should head down this road. Why ensure this separation? For starters, if you’re going to be sharing this with the rest of the world, and the core functionality doesn’t actually depend on Django, then you’ve broadened the audience. You’re also reducing yet another dependency in your package, which, even if you’re using it in Django projects, is another line of dependencies that can break. Where it makes sense, reference the standard library instead of Django utilities. If something moves in a new Django version, you’re now insulated from that change.

> It’s worth keeping in mind that you can add functionality to Django projects without Django-specific modules, or without necessarily requiring Django. In Chapter 16 on mixed dependency support, we’ll examine how to separate out what’s Django specific and what’s not.

## Drop Repository and Unit of Work?

While we don't need to entirely, the means of its implementation requires that we so drastically avoid Django's monolithic nature that the exercise loses its point and meaning.

## Barky Refactoring Roadmap

Dane Hillard's code focused on a command-line interface, but we will systematically refactor that code, across a series of branches, to do the following:

1. Replace the custom data handling (the DatabaseManager module) with the [Django O/RM](https://docs.djangoproject.com/en/5.0/topics/db/queries/)
   1. Replace the existing DatabaseManager with the Django ORM.
   1. Replace the CLI web-based REST API using the Django REST Framework.
   1. SOLID
   1. Use [DRF's testing facilities](https://www.django-rest-framework.org/api-guide/testing/#api-test-cases)
1. Adopt the suggestions from Percival and Gregory regarding the Unit of Work and Respository Pattern and Django: [Appendix D: Repository and Unit of Work Patterns with Django](https://www.cosmicpython.com/book/appendix_django.html)
   1. Add a separate Domain Model and explore the pros and cons of this: [Appendix D: Repository and Unit of Work Patterns with Django](https://www.cosmicpython.com/book/appendix_django.html)
1. Introduce messaging using Celery with Django. This will serve as a message bus to augment event-driven architecture.
   1. [Django is well supported using Celery](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html) as an asynchronous message/task queue.
   1. Reintroduce the [Command pattern](https://refactoring.guru/design-patterns/command) as a means to encapsule the transactional intent of messages passed within Celery.
1. Improve architecture:
   1. [CQRS in general](https://douwevandermeij.medium.com/the-repository-pattern-via-cqrs-with-python-django-elasticsearch-cb38437721d3) and in [Django](https://django-cqrs.readthedocs.io/en/latest/)
   1. Dependency injection - [A good overview](https://thinhdanggroup.github.io/python-dependency-injection/), [DI with specific Flask and Django examples](https://snyk.io/blog/dependency-injection-python/), and a [Comprehensive Python Dependency Injection Framework](https://python-dependency-injector.ets-labs.org/)

## Refactor to Assignments Map

1. Refactor 1 (DRF and ORM): Assignment 5
1. Refactor 2 (Repository Pattern and UoW ): Assignment 6
1. Refactor 3 (Celery/Messages and the Return of the Command): Assignment 7
1. Refactor 4 (CQRS and DI/Bootstrapping): Assignment 8
