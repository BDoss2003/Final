from __future__ import annotations
import abc
from django.db import transaction
from barky.adapters import repository


class AbstractUnitOfWork(abc.ABC):
    bookmarks: repository.AbstractRepository

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
        self.batches = repository.DjangoRepository()
        transaction.set_autocommit(False)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        transaction.set_autocommit(True)

    def commit(self):
        for batch in self.batches.seen:
            self.batches.update(batch)
        transaction.commit()

    def rollback(self):
        transaction.rollback()


class DjangoApiUnitOfWork(AbstractUnitOfWork):
    def __enter__(self):
        self.batches = repository.DjangoRepository()
        transaction.set_autocommit(False)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        transaction.set_autocommit(True)

    def commit(self):
        for batch in self.batches.seen:
            self.batches.update(batch)
        transaction.commit()

    def rollback(self):
        transaction.rollback()
