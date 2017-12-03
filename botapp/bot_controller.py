from slackclient import SlackClient

from botapp.models import WorkSpace, LeaveMessageAsk, LeaveMessageResponse


class BotController:

    def handle_leave_message_answer(self, event_message, team_id):

        workspace = WorkSpace.objects.get(team_id=team_id)
        client = SlackClient(workspace.bot_access_token)

        if LeaveMessageAsk.objects.filter(ts=event_message.get('thread_ts')).exists():  # check object exist
            leave_message_ask = LeaveMessageAsk.objects.get(ts=event_message.get('thread_ts'))
            converst_open_resp = client.api_call('conversations.open',
                                                 users=leave_message_ask.user_id)

            LeaveMessageResponse.objects.create(user_id=event_message.get('user'),
                                                ts=event_message.get('ts'),
                                                message_text=event_message.get('text'),
                                                leave_messake_ask=leave_message_ask)

            answer = '<@{}>  ответил на ваш запрос: "<{}>" - {}'.format(event_message.get('user'),
                                                                        leave_message_ask.message_text,
                                                                        event_message.get('text'))

            client.api_call('chat.postMessage',
                            channel=converst_open_resp['channel']['id'],
                            text=answer)

    def handle_command(self, slack_message):

        workspace = WorkSpace.objects.get(team_id=slack_message.get('team_id'))
        anounce_channel = workspace.announcing_channel_name
        if anounce_channel is None:
            anounce_channel = 'general'
        bot_text = "<@{}> нужно  отлучиться '{}'".format(slack_message['user_name'], slack_message.get('text'))

        bot_message_response = SlackClient(workspace.bot_access_token).api_call(method='chat.postMessage',
                                                                                channel=anounce_channel,
                                                                                text=bot_text)

        LeaveMessageAsk.objects.create(user_name=slack_message.get('user_name'),
                                       user_id=slack_message.get('user_id'),
                                       ts=bot_message_response['ts'],
                                       channel_id=bot_message_response['channel'],
                                       message_text=slack_message.get('text'),
                                       workspace=workspace)

    def get_available_channels_names(self, bot_access_token):
        all_channels = SlackClient(bot_access_token).api_call(
            'channels.list'
        )
        all_channels = [channel["name_normalized"] for channel in all_channels['channels']]
        return all_channels

    def get_available_channels(self, bot_access_token):
        all_channels = SlackClient(bot_access_token).api_call(
            'channels.list'
        )
        all_channels = [(channel["id"], channel["name_normalized"]) for channel in all_channels['channels']]
        return all_channels
