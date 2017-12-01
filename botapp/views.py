import json

from django.http import HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from botapp.bot_controller import BotController
from botapp.models import WorkSpace

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
bot_controller = BotController()


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


class SlashCommands(APIView):
    def post(self, request, *args, **kwargs):
        slack_message = request.data

        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        bot_controller.handle_command(slack_message)

        return Response(status=status.HTTP_200_OK)


class Events(APIView):
    def post(self, request, *args, **kwargs):

        slack_message = request.data

        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # verification challenge
        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)

        if 'team_id' in slack_message:

            if 'event' in slack_message:  # 4
                event_message = slack_message.get('event')

                # ignore bot's own message
                if event_message.get('subtype') == 'bot_message':  # 5
                    return Response(status=status.HTTP_200_OK)

                bot_controller.handle_leave_message_answer(event_message)

        return Response(status=status.HTTP_200_OK)
