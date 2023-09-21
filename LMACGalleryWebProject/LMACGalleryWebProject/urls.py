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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from lilChecker.views import lilCheckerMainView
from lmacAPI import views
from lmacNews.views import lmacNewsIndexView
from lmacWinners.views import lmacWinnersView
from lilGallery.views import lilGalleryMainAppView, lilGalleryAjaxAppView, lilGalleryImageMainAppView, \
    lilGalleryImageAjaxAppView, lilGalleryAjaxCommand, lilGalleryTagsView, lilGalleryAllTagsView
from lmacPoll.views import lmacPollMainAppView, lmacPollView, lmacPollCreatePollView, lmacPollAjaxCommand
from staticContentApp.views import staticContentAppViewRouter

admin.site.site_header = 'LMAC Website Admin'
admin.site.site_title = "LMAC"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('NOT PUBLIC', views.LMACApiV1LILView.as_view()),
    path('NOT PUBLIC2', views.LMACApiV1LMACView.as_view()),
    path('lmac-polls', lmacPollMainAppView),
    path('lmac-polls-create', lmacPollCreatePollView),
    path('lmac-poll-ajax-command', lmacPollAjaxCommand),
    path('lmac-poll/@<str:author>/<str:permlink>', lmacPollView),
    path('lil-gallery-ajax-image', lilGalleryImageAjaxAppView),
    path('lil-gallery-image/<int:imageId>', lilGalleryImageMainAppView),
    path('lil-gallery-ajax', lilGalleryAjaxAppView),
    path('lil-gallery-ajax-command', lilGalleryAjaxCommand),
    path('lil-gallery/', lilGalleryMainAppView),
    path('lil-gallery/<str:searchTerms>', lilGalleryMainAppView),
    path('lil-gallery/<str:searchTerms>/<int:page>', lilGalleryMainAppView),
    path('lil-gallery-tags', lilGalleryTagsView),
    path('lil-gallery-tags/all', lilGalleryAllTagsView),
    path('page/<slug:contentId>', staticContentAppViewRouter),
    path('home', staticContentAppViewRouter),
    path('lmac-winners', lmacWinnersView),
    path('lmac-winners/<int:contestId>', lmacWinnersView),
    path('lil-checker', lilCheckerMainView),
    path('lmac-news', lmacNewsIndexView),
    path('', staticContentAppViewRouter)

]


