import json

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, UpdateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from botapp.bot_controller import BotController
from botapp.models import WorkSpace
from .forms import UserForm, ChannelConfigForm, AddModeratorForm

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
bot_controller = BotController()


def slack_oauth_view(request):
    code = request.GET['code']
    print(code)
    params = {
        'code': code,
        'client_id': settings.SLACK_CLIENT_ID,
        'client_secret': settings.SLACK_CLIENT_SECRET
    }
    url = 'https://slack.com/api/oauth.access'
    data = json.loads(requests.get(url, params).text)
    try:
        WorkSpace.objects.get_or_create(team_id=data['team_id'],
                                        team_name=data['team_name'],
                                        bot_user_id=data['bot']['bot_user_id'],
                                        bot_access_token=data['bot']['bot_access_token'],
                                        user_admin=request.user)
    except IntegrityError:
        return render(request,
                      'botapp/workspaces_list.html',
                      {'error_message': 'Ошибка :(, кажется, кто то уже зарегестрировался как админ, этого сообщества'})
    return redirect('home')


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

            if 'event' in slack_message:
                event_message = slack_message.get('event')

                # ignore bot's own message
                if event_message.get('subtype') == 'bot_message':
                    return Response(status=status.HTTP_200_OK)

                bot_controller.handle_leave_message_answer(event_message, slack_message['team_id'])

        return Response(status=status.HTTP_200_OK)


class WorkspacesList(ListView):
    template_name = 'botapp/workspaces_list.html'
    context_object_name = 'workspaces'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return render(request, 'botapp/login.html')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return WorkSpace.objects.filter(user_admin=self.request.user)


class WorkspaceDetail(DetailView):
    template_name = 'botapp/workspace_detail.html'
    model = WorkSpace

    def get_context_data(self, **kwargs):
        context = super(WorkspaceDetail, self).get_context_data(**kwargs)
        workspace = WorkSpace.objects.get(pk=self.kwargs['pk'])
        context["channels"] = bot_controller.get_available_channels_names(workspace.bot_access_token)
        return context


class ChannelConfig(UpdateView):
    form_class = ChannelConfigForm
    model = WorkSpace
    template_name = 'botapp/channel_config.html'
    success_url = '/'

    def get_form_kwargs(self):  # put channels to form
        kwargs = super(ChannelConfig, self).get_form_kwargs()
        workspace = WorkSpace.objects.get(pk=self.kwargs['pk'])
        channels = bot_controller.get_available_channels(workspace.bot_access_token)
        kwargs['channels'] = channels
        return kwargs


class ModerAdd(UpdateView):
    template_name = 'botapp/moder_add.html'
    form_class = AddModeratorForm
    success_url = '/'
    model = WorkSpace


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'botapp/workspaces_list.html')
    context = {"form": form, }
    return render(request, 'botapp/register.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'botapp/workspaces_list.html',
                              {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'botapp/login.html', {'error_message': 'Invalid login'})
    return render(request, 'botapp/login.html')


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'botapp/login.html', context)
