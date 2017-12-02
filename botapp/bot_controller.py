import json

from slackclient import SlackClient

from botapp.models import WorkSpace, LeaveMessageAsk, LeaveMessageResponse


class BotController:

    def __init__(self):
        self.slack_client = SlackClient("xoxb-278092113248-OdY1DLMr1PIXpFco7P6sl1a2")  # TODO replace

    def handle_leave_message_answer(self, event_message):
        if LeaveMessageAsk.objects.filter(ts=event_message.get('thread_ts')).exists():  # check object exist
            leave_message_ask = LeaveMessageAsk.objects.get(ts=event_message.get('thread_ts'))
            converst_open_resp = self.slack_client.api_call('conversations.open',
                                                            users=leave_message_ask.user_id)

            LeaveMessageResponse.objects.create(user_id=event_message.get('user'),
                                                ts=event_message.get('ts'),
                                                message_text=event_message.get('text'),
                                                leave_messake_ask=leave_message_ask)

            answer = '<@{}>  ответил на ваш запрос: "<{}>" - {}'.format(event_message.get('user'),
                                                                        leave_message_ask.message_text,
                                                                        event_message.get('text'))
            self.slack_client.api_call('chat.postMessage',
                                       channel=converst_open_resp['channel']['id'],
                                       text=answer)

    def handle_command(self, slack_message):
        print(slack_message)

        workspace = WorkSpace.objects.get(team_id=slack_message.get('team_id'))
        anounce_channel = workspace.announcing_channel_name
        if anounce_channel is None:
            anounce_channel = 'general'
        bot_text = "<@{}> нужно  отлучиться '{}'".format(slack_message['user_name'], slack_message.get('text'))
        bot_message_response = self.slack_client.api_call(method='chat.postMessage',
                                                          channel=anounce_channel,  # TODO remove hardcoded chanel
                                                          text=bot_text)

        LeaveMessageAsk.objects.create(user_name=slack_message.get('user_name'),
                                       user_id=slack_message.get('user_id'),
                                       ts=bot_message_response['ts'],
                                       channel_id=bot_message_response['channel'],
                                       message_text=slack_message.get('text'),
                                       workspace=workspace)

    def get_available_channels_names(self):
        all_channels = self.slack_client.api_call(
            'channels.list'
        )
        all_channels = [channel["name_normalized"] for channel in all_channels['channels']]
        return all_channels

    def get_available_channels(self):
        all_channels = self.slack_client.api_call(
            'channels.list'
        )
        all_channels = [(channel["id"], channel["name_normalized"]) for channel in all_channels['channels']]
        return all_channels
