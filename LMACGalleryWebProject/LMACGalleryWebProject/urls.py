"""LMACGalleryWebProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path

from lilGallery.views import lilGalleryMainAppView, lilGalleryAjaxAppView, lilGalleryImageMainAppView, \
    lilGalleryImageAjaxAppView
from staticContentApp.views import staticContentAppViewRouter

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lil-gallery-ajax-image', lilGalleryImageAjaxAppView),
    path('lil-gallery-image/<int:imageId>', lilGalleryImageMainAppView),
    path('lil-gallery-ajax', lilGalleryAjaxAppView),
    path('lil-gallery/', lilGalleryMainAppView),
    path('lil-gallery/<str:searchTerms>', lilGalleryMainAppView),
    path('lil-gallery/<str:searchTerms>/<int:page>', lilGalleryMainAppView),
    path('page/<slug:contentId>', staticContentAppViewRouter),
    path('home', staticContentAppViewRouter),
    path('', staticContentAppViewRouter)

]
