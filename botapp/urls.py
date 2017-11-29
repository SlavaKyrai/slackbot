from django.conf.urls import url

from botapp.views import slack_oauth_view, Events, SlackMainView

urlpatterns = [
    url(r'^oauth/$', slack_oauth_view),
    url(r'^events/', Events.as_view()),
    url(r'^', SlackMainView.as_view()),
]
