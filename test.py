import asyncio
import zmq.asyncio
from zmq.asyncio import Context

# manages message flow between publishers and subscribers
class HelloWorldMessage:
    def __init__(self, url='127.0.0.1', port='5555'):
        self.url = "tcp://{}:{}".format(url, port)
        self.ctx = Context.instance()

        # activate publishers / subscribers
        asyncio.get_event_loop().run_until_complete(asyncio.wait([
            self.pub_hello_world(),
            self.sub_hello_world(),
        ]))

    # generates message "Hello World" and publish to topic 'world'
    async def pub_hello_world(self):
        pub = self.ctx.socket(zmq.PUB)
        pub.bind(self.url)

        # message contents
        msg = "Hello World"
        print(msg)

        # keep sending messages
        while True:
            # --MOVED-- slow down message publication
            await asyncio.sleep(1) 

            # publish message to topic 'world'
            # async always needs `send_multipart()`
            await pub.send_multipart([b'world', msg.encode('ascii')])  # WRONG: bytes(msg)

    # processes message "Hello World" from topic 'world'
    async def sub_hello_world(self):
        sub = self.ctx.socket(zmq.SUB)
        sub.connect(self.url)
        sub.setsockopt(zmq.SUBSCRIBE, b'world')

        # keep listening to all published message on topic 'world'
        while True:
            msg = await sub.recv_multipart()
            # ERROR: WAITS FOREVER
            print('received: ', msg)

if __name__ == '__main__':
    HelloWorldMessage()
