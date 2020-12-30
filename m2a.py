import asyncio
import logging

import email
from email.message import Message

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import Envelope, Session, SMTP

import apprise

# from yaml import load, dump
from yaml import load


try:
    # from yaml import CLoader as Loader, CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    # from yaml import Loader, Dumper
    from yaml import Loader

from pathlib import Path
home_dir = str(Path.home())
try:
    with open(f'{home_dir}/.config/m2a/m2a.yaml', 'r') as file:
        config = load(file, Loader=Loader)
except Exception as e:
    print(e)
# print(config)

# from tools import message_to_display

log = logging.getLogger("smtphandler")


def message_to_display(message: Message):
    result = ''
    if message.is_multipart():
        for sub_message in message.get_payload():
            result += message_to_display(sub_message)
    else:
        result = f"Content-type: {message.get_content_type()}\n" \
                 f"{message.get_payload()}\n" + "*" * 76 + '\n'
    return result


async def consume(title, body):
    # Create an Apprise instance
    tg_auth = f"tgram://{config['telegram']['bot_token']}/{config['telegram']['chat_ids'][0]}"

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

    # print(apobj)

    # print('Consumer')
    # print(queue)
    # while True:
    #     try:
    #         i = await queue.get()
    #     except Exception as e:
    #         print(e)
    #     finally:
    #         print(f'Consumer {i}')
    #         queue.task_done()


class Handler:
    # def __init__(self):
    # super().__init__()
    # self.queue = queue
    # self.loop = loop

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope):
        # try:
        # await self.queue.put('Something')
        # notify = self.loop.create_task(consume('task'))

        # self.loop.gather(notify)

        message: Message = email.message_from_bytes(envelope.content)

        log.info('From: %s', message['From'])
        log.info('To: %s', message['To'])
        log.info('Subject: %s', message['Subject'])
        log.info('Message data:\n%s', message_to_display(message))

        print(f"From: {message['From']}")
        print(f"To: {message['To']}")
        print(f"Subject: {message['Subject']}")
        print(f"Message data:\n {message_to_display(message)}")

        await consume(title=f"SUBJECT: {message['Subject']}", body=f"Message data:\n {message_to_display(message)}")

        # await consume()
        # except queue.Full:
        #     return '451 Mail queue full'
        # print('Produced', self.queue)
        return '250 OK Message Accepted'


async def smtpd():
    import systemd.daemon

    HOSTNAME = ''
    PORT = int(config['m2a']['port'])

    cont = Controller(Handler(), hostname=HOSTNAME, port=PORT)
    cont.start()

    systemd.daemon.notify('READY=1')

    input(
        f"Server started on HOSTNAME='{HOSTNAME}' PORT={PORT}. Press Return to quit.\n")
    cont.stop()


async def main(loop):
    try:
        await smtpd()
    except Exception as e:
        print(e)

if __name__ == '__main__':

    # logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop=loop))
    try:
        # loop.run_until_complete(main(loop=loop))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
