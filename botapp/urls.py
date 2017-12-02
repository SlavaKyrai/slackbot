from django.conf.urls import url

from botapp.views import slack_oauth_view, Events, SlashCommands, register, logout_user, login_user, \
    WorkspacesList, WorkspaceDetail, ChannelConfig

urlpatterns = [
    url(r'^oauth/$', slack_oauth_view),
    url(r'^events/$', Events.as_view()),
    url(r'^commands/$', SlashCommands.as_view()),
    url(r'^register/$', register, name='register'),
    url(r'^login/$', login_user, name='login'),
    url(r'^logout/$', logout_user, name="logout"),
    url(r'^workspaces/(?P<pk>\d+)/$', WorkspaceDetail.as_view(), name="workspace_detail"),
    url(r'^workspaces/(?P<pk>\d+)/channel', ChannelConfig.as_view(), name="channel_cfg"),
]
