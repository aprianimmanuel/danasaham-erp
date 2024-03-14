from django.urls import path, include

urlpatterns = [
    # DTTOT Document API and any other app-specific URLs
    path('dttotdoc/', include('dttotDoc.urls')),
]
