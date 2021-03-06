"""mtt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from tournament import views
from tournament.admin import admin_site
from django.conf import settings
from django.urls import include, path
from django.views.decorators.cache import cache_page

from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/createround/<int:pk>/', views.CreateRoundView.as_view(), name='createround'),
    path('admin/', admin_site.urls),
    # path('', cache_page(30)(views.IndexView.as_view()), name='index'),
    # path('', views.IndexView.as_view(), name='index'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('player-registration/', views.PlayerRegistrationView.as_view(), name='player-registration'),
    path('thanks/', views.ThanksView.as_view(), name='thanks'),
    path('tables/', views.TablesView.as_view(), name='tables'),
]

# public page
if settings.PUBLIC_PAGE_CACHE_TIME is None:
    urlpatterns.append(path('', views.IndexView.as_view(), name='index'))
else:
    urlpatterns.append(path('', cache_page(settings.PUBLIC_PAGE_CACHE_TIME)(views.IndexView.as_view()), name='index'))

# debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
