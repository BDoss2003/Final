from __future__ import annotations
import abc
from django.db import transaction
from barkyarch.adapters import repository


class AbstractUnitOfWork(abc.ABC):
    bookmarks: repository.AbstractRepository

    # __enter__ and __exit__ methods are used to create a context manager
    # https://www.pythonmorsels.com/every-dunder-method/#context-managers
    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class DjangoUnitOfWork(AbstractUnitOfWork):
    def __enter__(self):
        self.bookmarks = repository.DjangoRepository()
        # Django ORM has its own transaction management system - https://docs.djangoproject.com/en/5.0/topics/db/transactions/
        # will not be following P&G's advice to use transaction.set_autocommit(False)
        # we will be using Django's transaction.atomic() context manager instead
        # https://docs.djangoproject.com/en/5.0/topics/db/transactions/#controlling-transactions-explicitly

        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)

    def commit(self):
        # explicit rollback and commits are not normally needed in the Django ORM

        with transaction.atomic():
            for bm in self.bookmarks.bookmarks_set:
                print(f"committing bookmark: {str(bm)}")
                self.bookmarks.update(bm)

    def rollback(self):
        # explicit rollback and commits are not normally needed in the Django ORM
        # we will be using Django's transaction.atomic() context manager instead
        pass


class DjangoApiUnitOfWork(AbstractUnitOfWork):
    def __enter__(self):
        # self.batches = repository.DjangoRepository()
        # transaction.set_autocommit(False)
        # return super().__enter__()
        pass

    def __exit__(self, *args):
        # super().__exit__(*args)
        # transaction.set_autocommit(True)
        pass

    def commit(self):
        super.commit()
        pass

    def rollback(self):
        # transaction.rollback()
        pass
