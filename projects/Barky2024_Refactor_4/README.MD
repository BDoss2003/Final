# Barky Refactor 4

The final steps are to consider three things from P&G's APP:

- External message bus
- Dependency Injection
- Bootstrapping

## External Message Bus

By now, I've adopted a familiar pattern where I use any excuse to just revert to things that are friendly to the Django monolithic architecture, which is fine.  Django is stable, relatively older, and qualifies as [boring tech](https://mcfunley.com/choose-boring-technology).  It is imporant to be warying of reinventing the wheel, but to also be aware of how (and why) a monolith like Django does implement [Patterns of Enterprise Application Architecture](https://martinfowler.com/eaaCatalog/index.html).

### Django Channels

While [Django Channels](https://channels.readthedocs.io/en/latest/) is not a native project within the Django Project itself, it is highly adjacent (like the [Django Rest Framework](https://www.django-rest-framework.org/) is) and will likely remain consistent with Django for years to come.

We're really going to rely on Django Channels to model its ability to broker background tasks in the same way that Celery can do. Channels would also let us do external message bus actions as well.

Here is a useful example from Jay Hale: [https://github.com/jayhale/channels-examples-bg-task](https://github.com/jayhale/channels-examples-bg-task)

#### Redis

Almost all task/messaging frameworks end up wanting you to install/use [REDIS](https://redis.io/).  It has turned out to be almost impossible in the Django/Python world to avoid this.  Even Channels, which does have an in-memory facility for its backend, won't serve as an implementation for P&G's external message bus without [REDIS](https://redis.io/).

So, there are two things here, depending on your OS:

1. REDIS will very happly/handily install on [Linux](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/) or [Mac](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-mac-os/) without much hassle.
1. [REDIS on Windows](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/) isn't necessarily hard, but requires Win10/11 and to "fake" a \*nix environment.

### Worker and Background Tasks in Channels

One of the issues in making our project work using Django Channels is that we are using the Worker and Background Tasks in Django Channels to simulate the external message bus as is in P&G.  Django Channels does this task just okay, but is flexible to do external messaging as well.  For the P&G case, the aim was InterProcess Communication within a wider system.

The issue with REDIS, as stated in the previous section, comes from the following warning from the Django Channels documentation:

> The worker/background tasks system in Channels is simple and very fast, and achieves this by not having some features you may find useful, such as retries or return values. We recommend you use it for work that does not need guarantees around being complete (at-most-once delivery), and for work that needs more guarantees, look into a separate dedicated task queue. **This feature does not work with the in-memory channel layer.**

So, it is the use of Channel Layers that forces us to us REDIS.  In this regard, we could have gone the Celery route.

## Dependency Injection

Neither Python nor Django have a native facility for [Dependency Injection](https://martinfowler.com/articles/injection.html), which is also often called the [Inversion of Control](https://en.wikipedia.org/wiki/Dependency_inversion_principle).

Dependency Injection is among the 5 SOLID principles, each of which we would have studied closer had the book been available to me.

However, here they are:

- [Single Responsibility Principle](https://en.wikipedia.org/wiki/Single_responsibility_principle)
- [Open-Close Princple](https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle)
- [Liskov Substitution Principle](https://en.wikipedia.org/wiki/Liskov_substitution_principle)
- [Interface Segregation Principle](https://en.wikipedia.org/wiki/Interface_segregation_principle)
- [Dependcy Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)

With DI, we are doing this:

We use the dependency inversion principle to address potential coupling issues. Looseness of coupling allows for parts of a system to evolve independently.  When two software modules depend on each other, Dependency Injection holds that we should consider relationships between higher-level modules that specify **WHAT** will happen, and lower-level modules that will specify **HOW** something will happen.  With dependency injection,  the goal is to separate higher-level modules from keeping track of (or being responsible for) the low-level module implementation details. Thus, the goals of DI are:

- High-level modules should not import anything from low-level modules and instead rely on abstractions. The Commands are designed this way in our project.
- Abstractions (higher level) should not depend on details but rather the details (lower-level) should depend on abstractions.

If both higher-level and lower-level objectsdepend on the same abstractions we invert how the depency is specified - You'll be driving a rental car, but which actual car you get is dependency that is `injected` at the time of rental car checkin.

Dependency Injection informs the design of interactions between higher-level and lower-level modules where the details of this interaction are abstracted. The lower-level module is designed purposefully to know about the **WHAT** as the **HOW** is immaterial: the expected result will be assured.

The linked Wiki article diagrams the differences thusly:

A straightforward pattern can be seen here, but one where the dependencies are all rigid:

![Traditional Approach](../../docs/img/Traditional_Layers_Pattern.png)

A Dependency Inversion approach can be seen here:

![DIP Approach](../../docs/img/DIPLayersPattern.png)

For this refactor, I am using a Python Dependency Injector framework, called (handily) [Python Injector](https://github.com/python-injector/injector).

### DI with the Commands

The previous refactor switched to commands and this refactor will utilize the ABC-designed Command (slightly modifed from Dane Hillard) to facilitae the injection.

## Bootstrapping

While P&G add some system boostrapping in Chapter 13, with Django's monolith, this is all handled by both the manage.py and settings.py files in terms of getting Django's ecosystem to launch.  As P&G use Flask based on the premise that their book will cover the development of a Microservices architecture, then it is understandable that they must also include this **bootstrapping** provision in their work.  However, this is just not necessary in Django.

The [following has been said](https://learndjango.com/tutorials/flask-vs-django) about Django vs. Flask when it comes to a microservices vs. monolithing dichotomy:

> A Django proponent would say that a Flask developer eventually rebuilds Django itself, poorly and slowly. A Flask advocate would counter that Django is far too heavy, slower for prototypes, and harder to customize as needed at scale.

I would appeal to the [Pareto Principle](https://www.investopedia.com/terms/1/80-20-rule.asp) here and say that I'd build my castle on the foundation of the tried-and-true like Django and then consider further. But don't forget, as I myself have grown older, I increasingly stand by the wisdom of [choosing boring technology](https://mcfunley.com/choose-boring-technology).

In short, we don't need P&G's bootstrapping.

## New to Refactor 4

- For simplicity, I'll be using Django Channels rather than Celery. Celery is very standard, but has too many dependencies for our purposes.
- As we are moving entirely into the Django monolith, remeber to remove the editable package: `pip uninstall barky`
-

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
1. Refactor 3 (Django Signals and the Return of the Command): Assignment 7
1. Refactor 4 (Django Channels to approximate CQRS and DI/Bootstrapping): Assignment 8
