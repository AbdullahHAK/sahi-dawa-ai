"""Shared FastAPI dependencies: a process-wide catalogue repository singleton."""

from functools import lru_cache

from app.services.catalogue import CatalogueRepository, default_catalogue_path


@lru_cache(maxsize=1)
def get_catalogue_repository() -> CatalogueRepository:
    return CatalogueRepository.from_csv(default_catalogue_path())
