import json

from django.http import HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from slackclient import SlackClient

from botapp.models import WorkSpace

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
Client = SlackClient("xoxb-278092113248-NNxvSizjQbxYpt15j95Mpj3Y")  # TODO replace with token after oauth


class SlackMainView(TemplateView):
    template_name = 'botapp/index.html'


def slack_oauth_view(request):
    code = request.GET['code']
    params = {
        'code': code,
        'client_id': settings.SLACK_CLIENT_ID,
        'client_secret': settings.SLACK_CLIENT_SECRET
    }
    url = 'https://slack.com/api/oauth.access'
    data = json.loads(requests.get(url, params).text)
    WorkSpace.objects.get_or_create(team_id=data['team_id'],
                                    team_name=data['team_name'],
                                    bot_user_id=data['bot']['bot_user_id'],
                                    bot_access_token=data['bot']['bot_access_token'])
    print(data)
    return HttpResponse('Success')


class Events(APIView):
    def post(self, request, *args, **kwargs):

        slack_message = request.data
        print(request.data)

        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # verification challenge
        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)

        ## handle command
        if 'command' in slack_message:
            bot_text = "<@{}> нужно  отлучиться '{}'".format(slack_message['user_name'], slack_message.get('text'))
            Client.api_call(method='chat.postMessage',
                            channel="general",  # TODO remove hardcoded chanel
                            text=bot_text)
        return Response(status=status.HTTP_200_OK)
