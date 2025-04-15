from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar, cast

from django.urls import URLResolver, path  #type: ignore # noqa: PGH003
from rest_framework.routers import SimpleRouter  #type: ignore # noqa: PGH003
from rest_framework.viewsets import (  #type: ignore # noqa: PGH003
    GenericViewSet,
    ViewSet,
)

T = TypeVar("T", bound=Any)


@dataclass
class CustomViewRouter:
    """Router for APIView and ViewSet."""

    url_prefix: str = ""

    _drf_router: SimpleRouter = field(default_factory=SimpleRouter)
    _paths: list[URLResolver] = field(default_factory=list)

    def register(  # noqa: PLR0913
        self,
        route: str,
        view: T,  # noqa: ARG002
        name: str | None = None,
        basename: str | None = None,
        as_view_kwargs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Callable[[T], T]:
        route = f"{self.url_prefix}{route}"

        def decorator(view: T) -> T:
            if issubclass(view, (ViewSet, GenericViewSet)):
                kwargs.setdefault("basename", basename or name)
                self._drf_router.register(route, view, **kwargs)
            elif name:
                self._paths.append(
                    path(route, view.as_view(**(as_view_kwargs or {})), name=name),
                )
            else:
                self._paths.append(
                    path(route, view.as_view(**(as_view_kwargs or {})), **kwargs),
                )
            return cast(T, view)

        return decorator

    def register_decorator(  # noqa: ANN201
        self,
        route: str,
        name: str | None = None,
        basename: str | None = None,
        as_view_kwargs: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        def decorator(view: T) -> T:
            self.register(
                route,
                view,
                name=name,
                basename=basename,
                as_view_kwargs=as_view_kwargs,
                **kwargs,
            )
            return view

        return decorator

    @property
    def urls(self) -> list[Any]:
        return self._paths + self._drf_router.urls
