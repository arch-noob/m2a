#!/usr/bin/env python

import signal
import asyncio
import logging

import email
from email.message import Message

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import Envelope, Session, SMTP

import apprise

log = logging.getLogger("smtphandler")


class Notification:

    def _default_configuration_file(self):
        from pathlib import Path
        home_dir = str(Path.home())
        config_file = f'{home_dir}/.config/m2a/m2a.yaml'
        return config_file

    def _default_configuration(self):
        # from yaml import load, dump
        from yaml import load

        try:
            # from yaml import CLoader as Loader, CDumper as Dumper
            from yaml import CLoader as Loader
        except ImportError:
            # from yaml import Loader, Dumper
            from yaml import Loader

        try:
            with open(self.config_file, 'r') as file:
                config = load(file, Loader=Loader)
                return config
        except Exception as e:
            print(
                f'Configuration file could not be found @ "{self._default_configuration_file()}".')
            print(
                'Example configuration could be copied from "/usr/share/m2a/m2a.yaml.example".')

    def __init__(self):
        self.config_file = self._default_configuration_file()
        self.config = self._default_configuration()

    def info(self):
        return self.config, self.config_file

    async def send(self, title, body):
        self.send_sync(title, body)

    def send_sync(self, title, body):
        # Create an Apprise instance
        tg_auth = f"tgram://{self.config['telegram']['bot_token']}/{self.config['telegram']['chat_ids'][0]}"

        asset = apprise.AppriseAsset(async_mode=False)
        apobj = apprise.Apprise(asset=asset)

        # You can mix and match; add an entry directly if you want too
        # In this entry we associate the 'admin' tag with our notification
        apobj.add(
            tg_auth, tag='admin')

        apobj.notify(
            body=body,
            title=title,
        )

    def daemon_start(self):
        if self.config['m2a']['notify']['on_start']:
            self.send_sync(title='M2A Daemon Started',
                           body='All Systems Nominal')

    def daemon_stop(self):
        if self.config['m2a']['notify']['on_stop']:
            self.send_sync(title='M2A Daemon Stopped', body='')


def message_to_display(message: Message):
    result = ''
    if message.is_multipart():
        for sub_message in message.get_payload():
            result += message_to_display(sub_message)
    else:
        result = f"Content-type: {message.get_content_type()}\n" \
                 f"{message.get_payload()}\n" + "*" * 76 + '\n'
    return result


class Handler:

    def __init__(self, notify: Notification):
        super().__init__()
        self.notify = notify
        # self.loop = loop

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope):
        message: Message = email.message_from_bytes(envelope.content)

        log.info('From: %s', message['From'])
        log.info('To: %s', message['To'])
        log.info('Subject: %s', message['Subject'])
        log.info('Message data:\n%s', message_to_display(message))

        print(f"From: {message['From']}")
        print(f"To: {message['To']}")
        print(f"Subject: {message['Subject']}")
        print(f"Message data:\n {message_to_display(message)}")

        # await Notification().send(title=f"SUBJECT: {message['Subject']}", body=f"Message data:\n {message_to_display(message)}")
        await self.notify.send(title=f"SUBJECT: {message['Subject']}", body=f"Message data:\n {message_to_display(message)}")

        return '250 OK Message Accepted'


async def smtpd(notify):
    import systemd.daemon

    HOSTNAME = ''
    PORT = int(notify.config['m2a']['port'])

    try:

        cont = Controller(Handler(notify), hostname=HOSTNAME, port=PORT)
        cont.start()

        systemd.daemon.notify('READY=1')

        notify.daemon_start()

        # n = Notification()
        # if n.config['m2a']['notify']['on_start']:
        #     await n.send(title='M2A Daemon Started', body='All systems nominal')

        input(
            f"Server started on HOSTNAME='{HOSTNAME}' PORT={PORT}. Press Return to quit.\n")
        cont.stop()
    except Exception as e:
        print('Error starting daemon:', e, '\n')
        if e.errno == 98:
            print('Please try to bind config to other PORT.')
            print(f'Config: {notify.config_file}')
            print('Variable: "m2a.PORT"')
        systemd.daemon.notify('READY=0')
        cont.stop()
    # finally:


class GracefulKiller:

    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


notify = Notification()


async def main(loop):
    try:
        await smtpd(notify)
        # notify.daemon_start()
    except Exception as e:
        print(e)


if __name__ == '__main__':

    killer = GracefulKiller()

    loop = asyncio.get_event_loop()

    while not killer.kill_now:

        # n = Notification()

        # print(n.info())

        # logging.basicConfig(level=logging.DEBUG)
        # loop.create_task(main(loop=loop))
        try:
            loop.run_until_complete(main(loop=loop))
            # loop.run_forever()
        except KeyboardInterrupt:
            pass

    loop.stop()

    notify.daemon_stop()
