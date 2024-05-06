# Barky Refactor 2
The major difference in this refactor is the inclusion of a few key concepts which are explored in depth in P&G:
- **Repository**: by abstracting state change operations on the entities within the domain, we can replace/insert any number of data persistence strategies.
    - P&G Readings: Chapters 2-5
- **Unit of Work**: The unit of work is a means of encapsulating and describing transation-like operations with your system such that any number of needed operations can be coordinated and completed that, collectively constitude an whole operation's completion.  In effect, this is more-or-less the equivalent of a database transaction.
    - P&G Readings: Chapters 6 and 7.
- Project structure with setuptools
- Use of `unittest` rather than `pytest`.

## New to Refactor 2
- Considers the Project Stucture Template from P&G from [Appendix B](https://www.cosmicpython.com/book/appendix_project_structure.html)
    - Key items here are the use of Python's [setuptools](https://setuptools.pypa.io/en/latest/setuptools.html) to make the entire application installable.  This makes references within the application easier
- Considers the [Appendix D](https://www.cosmicpython.com/book/appendix_django.html) application structure from P&G.
    - this utilizes the app structure form Appendix B to have `barky` (allocation for P&G) live alongside the Django app
    - it is not 100% certain that we'd completely live with this architecture - we might just collapase back into Django's folder/project strcuture.
- **NOTE**: we are NOT using Docker despite P&G using it (and many other Django and Python books/tutorials).  Docker is just an extra layer that I chose not to deal with as our virtual environment will be sufficient.
- **CAUTION**: the django parts are NOT launched automatially and need to be manually launched in thie refactor.  So you make sure you use one terminal to launch the django app so that another can be used to run tests in `barky`
- With this refactor's architecture, we could use the Django project directly OR the barky infrastructure as barky has been refactored to be available for other implementation strategies beyond just Django.
    - P&G presume the use of [pytest](https://docs.pytest.org/en/8.0.x/), but we'll stick to the built-in [unittest](https://docs.python.org/3/library/unittest.html) that comes with Python to remain consistent with Django.  So, new tests will be included to only test 'barky' rather than Django.  Thus, the Django parts will continue self-contain its tests.

## Key steps for this refactor

**KEY NOTE**: In keeping with P&G, we've moved the code to a `src/` directory.  However, I've not placed the `tests/` directly outside of source.  This has to do with the nature of Django and its clear that P&G warn us in [Appendix D](https://www.cosmicpython.com/book/appendix_django.html) that we will indeed be fighting Django to make **some** aspects of their architecture work. This is not unlike adopting a major [CRM](https://en.wikipedia.org/wiki/Customer_relationship_management) (such as [Salesforce](https://en.wikipedia.org/wiki/Salesforce)) or [ERP](https://en.wikipedia.org/wiki/Enterprise_resource_planning) platform and then trying to fit it alongside other elements of your enterprise architecture - it can be done, but it has to be done in conjunction with the behaviors of that major platform.

1. make sure you configure the `setup.py` file, which is used by [setuptools](https://pypi.org/project/setuptools/).
2. make sure you "install" the package from the directory just above `src/` using the following command: `pip install -e src/` 
3. take note of what I do in the code to make Django work outside of its own environment. See: [Django Settings](https://docs.djangoproject.com/en/5.0/topics/settings/).  
4. The path/location information is hard-wired, so it might have to be changed on your machine.
5. Unit tests are run this way: `python -m unittest -v test_services.TestCaseRepository.test_repository_list`

### We Won't Continue Down this Path
We will not likely put the effort into the CRUD (repository pattern) and transaction (Unit Of Work) facilities of the architectural patterns from chapters 1 to 7 with Django as features or facilities that exist **OUTSIDE** of the Django project framework.  This is because we are fundamentally fighting Django to get these done.  This is probably why P&G chose Flask/SQLAlchemy as they are more loosely coupled which makes it easier to include them as part of an overall architecture.

However, we can more readily and easily implement these within the Django project structure.  While this is indeed feasible, it lessens the impact and advantage of the pattern as we are not truly independent of Django.  There are valid workarounds, but they stray back into the territory of fighting the intrinsic design of the Django Framework.

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

P&G discuss the ins and outs of Django app architecture and refer to [this post](https://forum.djangoproject.com/t/where-to-put-business-logic-in-django/282/7) on the matter of how to extend/modify Django's out-of-the-box design when/as needed.  Of course, the book's [Epilogue](https://www.cosmicpython.com/book/epilogue_1_how_to_get_there_from_here.html) is also a great read on the matter of how to balance and make sense out of the book's material.

### Repository Pattern and Django

There are some articles and resources that demonstrate implementing the Repository Pattern in Django (or argue against them):
- **P&G**: [Appendix D](https://www.cosmicpython.com/book/appendix_django.html) has quite a bit of valuable discussion on the the topic in addition to the sample code given.
- [Arjun Adhikari | Python is Love](https://pythonislove.com/repository-design-pattern-in-django) provides a nice walkthrough with some useful code examples.
- [Roy Manigley | Django Repository Pattern](https://github.com/roymanigley/django-repository-pattern) - this is one of the more straight-foward approaches you can use.
- [James Bennet | Against service layers in Django](https://www.b-list.org/weblog/2020/mar/16/no-service/) - the argument against bothing with service layers such as the repository and UoW patterns.  Don't forget, Django is the "monolith."  
- [Luke Plant | Django Views - The Right Way](https://spookylukey.github.io/django-views-the-right-way/index.html) In the end, any service layer is activated/engaged from views: [there are many practices to consider when it comes to handling view design](https://spookylukey.github.io/django-views-the-right-way/index.html).
- [Douwe va der Meij | The repository pattern via CQRS with Python/Django/Elasticsearch](https://douwevandermeij.medium.com/the-repository-pattern-via-cqrs-with-python-django-elasticsearch-cb38437721d3) - a full treatment that looks forward.

### Unit of Work and Django
- [sepehr akbarzadeh | Revolutionize Your Data Handling with the Unit of Work Design Pattern in Python and Django](https://python.plainenglish.io/revolutionize-your-data-handling-with-the-unit-of-work-design-pattern-in-python-and-django-14895d147cdc) - Good overview article.
- [Manuel Kanetscheider | A Python Implementation of the Unit of Work and Repository Design Pattern using SQLModel](https://dev.to/manukanne/a-python-implementation-of-the-unit-of-work-and-repository-design-pattern-using-sqlmodel-3mb5) - also a good overview.
- [Transactions in Django](https://docs.djangoproject.com/en/5.0/topics/db/transactions/) - the Unit of Work is an abstraction for transaction management, which Django does natively.

## Barky Refactoring Roadmap
Dane Hillard's code focused on a command-line interface, but we will systematically refactor that code, across a series of branches, to do the following:

1. Replace the custom data handling (the DatabaseManager module) with the [Django O/RM](https://docs.djangoproject.com/en/5.0/topics/db/queries/)
    1. Replace the existing DatabaseManager with the Django ORM.
    2. Replace the CLI web-based REST API using the Django REST Framework.
    3. SOLID
    4. Use [DRF's testing facilities](https://www.django-rest-framework.org/api-guide/testing/#api-test-cases)
2. Adopt the suggestions from Percival and Gregory regarding the Unit of Work and Respository Pattern and Django: [Appendix D: Repository and Unit of Work Patterns with Django](https://www.cosmicpython.com/book/appendix_django.html)
    1. Add a separate Domain Model and explore the pros and cons of this: [Appendix D: Repository and Unit of Work Patterns with Django](https://www.cosmicpython.com/book/appendix_django.html)
3. Introduce messaging using Celery with Django.  This will serve as a message bus to augment event-driven architecture.
    1. [Django is well supported using Celery](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html) as an asynchronous message/task queue.
    2. Reintroduce the [Command pattern](https://refactoring.guru/design-patterns/command) as a means to encapsule the transactional intent of messages passed within Celery.
4. Improve architecture:
    1. [CQRS in general](https://douwevandermeij.medium.com/the-repository-pattern-via-cqrs-with-python-django-elasticsearch-cb38437721d3) and in [Django](https://django-cqrs.readthedocs.io/en/latest/)
    2. Dependency injection - [A good overview](https://thinhdanggroup.github.io/python-dependency-injection/), [DI with specific Flask and Django examples](https://snyk.io/blog/dependency-injection-python/), and a [Comprehensive Python Dependency Injection Framework](https://python-dependency-injector.ets-labs.org/)


## Refactor to Assignments Map
1. Refactor 1 (DRF and ORM): Assignment 5 
2. Refactor 2 (Repository Pattern and UoW ): Assignment 6
3. Refactor 3 (Celery/Messages and the Return of the Command): Assignment 7
4. Refactor 4 (CQRS and DI/Bootstrapping): Assignment 8

## Refactoring Notes relative to APP
1. The [Command](https://refactoring.guru/design-patterns/command) pattern and Barky: Whereas Barky uses the `Command` design pattern, the Django Rest Framework's [ViewSet](https://www.django-rest-framework.org/api-guide/viewsets/) structure as a controller in the [Model View Controller](https://www.askpython.com/django/django-mvt-architecture) sense.  As such, the objective of the Command pattern - to achieve a separation of concerns such that all pathways to effect a state change in the application use the same facility - is achieved with the ViewSet acting as a controller.  A Django app's views module works with DRF's ViewSet to handle the same thing.  As such, we no longer require the Command module from Barky.

### Helpful Articles for this Refactor:
- [Gabriel Saldaña | How to use Django models in external Python scripts](https://blog.gabrielsaldana.org/using-django-models-in-external-python-scripts/) - Vital if we are going to leverage the Django ORM outside of Django - very [kludgey](https://en.wikipedia.org/wiki/Kludge), so not a long-term strategy.
- [Adam Green | aShould You Use Python pathlib or os?](https://betterprogramming.pub/should-you-be-using-pathlib-6f3a0fddec7e) - good for mapping between both approaches to working with path information.
- [SO | How to call django.setup() in console_script?](https://stackoverflow.com/questions/39704298/how-to-call-django-setup-in-console-script) - some useful examples of how to use some of the built-in methods.
- [Django Docs | How applications are loaded](https://docs.djangoproject.com/en/5.0/ref/applications/#how-applications-are-loaded) - working with `Django.setup()`, settings, and apps.
- The [unittest - unit testing framework](https://docs.python.org/3/library/unittest.html#) - built into Python.
- [Ivan Zakrevsky|About my experience of using Django Framework](https://emacsway.github.io/en/django-framework/) - good review of the Django experience with attention to how Django does not give us much room for the [Repository](https://emacsway.github.io/en/django-framework/#active-record) and [UoW](https://emacsway.github.io/en/django-framework/#transactional-consistency-of-data) patterns.
- [Jordi Fierro | Clean Architecture in Django](https://medium.com/21buttons-tech/clean-architecture-in-django-d326a4ab86a9) - Very good explanation of the Clean Architecture in Django - we end up writing around the framework.