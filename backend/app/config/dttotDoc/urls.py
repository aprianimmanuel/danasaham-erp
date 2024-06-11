from django.urls import path
from .views import DttotDocDetailView, DttotDocListView
from app.common.routers import CustomViewRouter

router = CustomViewRouter(url_prefix="api/")

router.register(
    route='dttotdocs/<uuid:document_id>/',
    view=DttotDocListView,
    name='dttot-doc-list'
)

router.register(
    route='dttotdocs/detail/<uuid:pk>/',
    view=DttotDocDetailView,
    name='dttot-doc-detail'
)

urlpatterns = router.urls
