from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from trading import views

urlpatterns = [
    url(r'^bot', views.bot),
    url(r'^capital', views.capital),
    url(r'^trade', views.trade),
    url(r'^portfolio', views.portfolio)
]

urlpatterns = format_suffix_patterns(urlpatterns)