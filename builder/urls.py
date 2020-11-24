from django.urls import path

from . import views

app_name = "builder"

urlpatterns = [
    path("<hash>/", views.draft, name="draft"),
    path("<hash>/search/<search_slug>/", views.search, name="search"),
    path("<hash>/no-search-term/", views.no_search_term, name="no-search-term"),
    path("<hash>/update/", views.update, name="update"),
    path("<hash>/search/", views.new_search, name="new-search"),
    path("<hash>/download.csv", views.download, name="download"),
    path("<hash>/download-dmd.csv", views.download_dmd, name="download-dmd"),
]
