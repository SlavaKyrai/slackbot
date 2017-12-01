import json

from django.http import HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from slackclient import SlackClient

from botapp.models import WorkSpace, LeaveMessageAsk

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
Client = SlackClient("xoxb-278092113248-OdY1DLMr1PIXpFco7P6sl1a2")  # TODO replace with token after oauth


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
        print("REQUEST DATA", request.data)

        workspace = WorkSpace.objects.get(
            team_id=slack_message.get('team_id'))  # be carefull with 1 workspace - 2 or more
        # bot id
        print(workspace)

        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # verification challenge
        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)

        ## handle command
        if 'command' in slack_message:
            bot_text = "<@{}> нужно  отлучиться '{}'".format(slack_message['user_name'], slack_message.get('text'))
            bot_message_response = Client.api_call(method='chat.postMessage',
                                                   channel="general",  # TODO remove hardcoded chanel
                                                   text=bot_text)

            LeaveMessageAsk.objects.create(
                user_name=slack_message.get('user_name'),
                user_id=slack_message.get('user_id'),
                ts=bot_message_response['ts'],
                channel_id=bot_message_response['channel'],
                message_text=slack_message.get('text'),
                workspace=workspace
            )
            print("BMR: ", bot_message_response)
        return Response(status=status.HTTP_200_OK)
