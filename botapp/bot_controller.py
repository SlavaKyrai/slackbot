from slackclient import SlackClient

from botapp.models import WorkSpace, LeaveMessageAsk, LeaveMessageResponse


class BotController:

    def __init__(self):
        self.slack_client = SlackClient("xoxb-278092113248-OdY1DLMr1PIXpFco7P6sl1a2")  # TODO replace

    def handle_leave_message_answer(self, event_message):
        if LeaveMessageAsk.objects.filter(ts=event_message.get('thread_ts')).exists():  # check object exist
            leave_message_ask = LeaveMessageAsk.objects.get(ts=event_message.get('thread_ts'))
            print("EVENT MESSAGE, NOT BOT", event_message)

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
        all_channels = self.slack_client.api_call(
            'channels.list'
        )
        print("Channels", all_channels)
        workspace = WorkSpace.objects.get(team_id=slack_message.get('team_id'))
        bot_text = "<@{}> нужно  отлучиться '{}'".format(slack_message['user_name'], slack_message.get('text'))
        bot_message_response = self.slack_client.api_call(method='chat.postMessage',
                                                          channel="general",  # TODO remove hardcoded chanel
                                                          text=bot_text)

        LeaveMessageAsk.objects.create(user_name=slack_message.get('user_name'),
                                       user_id=slack_message.get('user_id'),
                                       ts=bot_message_response['ts'],
                                       channel_id=bot_message_response['channel'],
                                       message_text=slack_message.get('text'),
                                       workspace=workspace)
