import asyncio
from threading import Thread
from hbmqtt.broker import Broker


class brokerServer():

    def __init__(self):
        self.broker = None
        self.config = {
            'listeners': {
                'default': {
                    'max-connections': 50000,
                    'bind': '0.0.0.0:1883',
                    'type': 'tcp',
                },
            },
            'plugins': [ 'auth_anonymous' ],
            'auth': {
                'allow-anonymous': True,
            },
            'topic-check': {
                'enabled': True,
                'plugins': ['topic_taboo'],
            },
        }

    async def broker_coroutine(self, config, loop):
        self.broker = Broker(config, loop)
        await self.broker.start()

    def start(self):
        loop = asyncio.new_event_loop()
        thread = Thread(target=lambda: self.run(loop))
        thread.start()

    def run(self, loop):
        try:
            future = asyncio.gather(self.broker_coroutine(self.config, loop),
                                    loop=loop,
                                    return_exceptions=True)
            loop.run_until_complete(future)
            loop.run_forever()
        except (Exception, KeyboardInterrupt):
            loop.close()
        finally:
            loop.run_until_complete(self.broker.shutdown())
            loop.close()
