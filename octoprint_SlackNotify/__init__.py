from __future__ import absolute_import, unicode_literals

import octoprint.plugin
from slackclient import SlackClient


class SlackNotifyPlugin(octoprint.plugin.EventHandlerPlugin,
                           octoprint.plugin.SettingsPlugin,
                           octoprint.plugin.TemplatePlugin):
    def get_settings_defaults(self):
        return dict(bot_token=None, channel_id=None)

    def _send_to_slack(self, message, media=None):
        token = self._settings.get(['bot_token'])
        recipient = self._settings.get(['channel_id'])
        if not token or not recipient:
            self._logger.warning('Slack settings misconfigured')
            return

        client = SlackClient(token)

        if media:
            result = client.api_call(
                "files.upload",
                channels=[recipient],
                file=open(media, 'rb'),
                title=message,
            )
        else:
            result = client.api_call(
                "chat.postMessage",
                channel=recipient,
                text=message,
            )


    def on_event(self, event, payload):
        if event == 'PrintStarted':
            message = 'Started printing %s' % payload['name']
            self._send_to_slack(message)
        elif event == 'PrintFailed':
            message = 'Failed to print %s after %s with reason: %s' % (
                payload['name'], payload['time'], payload['reason'])
            self._send_to_slack(message)
        elif event == 'PrintCancelling':
            message = 'Cancelled print %s with message: %s' % (
                payload['name'], payload['firmwareError'])
            self._send_to_slack(message)
        elif event == 'PrintDone':
            message = 'Finished printing %s total print time %s' % (
                payload['name'], payload['time'])
            self._send_to_slack(message)
        elif event == 'MovieDone':
            message = 'Finished rendering timelapse for %s' % payload['gcode']
            self._send_to_slack(message, payload['movie'])
        else:
            return

    def get_template_configs(self):
        return [
            dict(type="settings", name="Slack Notify", custom_bindings=False)
        ]


__plugin_implementation__ = SlackNotifyPlugin()
