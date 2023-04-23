import json
from .EPC04 import EPCDriver
from .server import MessageSender
import threading
from time import sleep


def remote_instrument(instrument, name):
    class RemoteInstrument(instrument):

        def __init__(self, hostname, local_name, remote_name):
            methods = filter(self._is_public_method, dir(self))
            for method in methods:
                setattr(self,
                        method,
                        self._remote_decorator(getattr(self, method)))
            self.hostname = hostname
            self.local_name = local_name
            self.remote_name = remote_name
            self.messenger = MessageSender(self.local_name, self.hostname)
            self.retrieve_thread = threading.Thread(
                name='retrieve',
                target=self._retrieve_messages,
                daemon=True)
            self.messages = []
            self.retrieve_thread.start()
            self.instrument_name = name
            print(self.instrument_name)

        def _send_message(self, message):
            return self.messenger.send_message(self.remote_name, message)

        def _retrieve_messages(self):
            while True:
                self.messages += [json.loads(message)
                                  for message in self.messenger.retrieve_messages()]
                sleep(0.01)

        def _is_public_method(self, member):
            is_method = callable(getattr(self, member))
            is_public = member[0] != '_'
            return is_method & is_public

        def _remote_decorator(self, func):
            def wrapper(*args, **kwargs):
                resp = self._call_remote_func(func.__name__, args, kwargs)
                return resp
            return wrapper

        def _call_remote_func(self, func_name, args, kwargs):
            unencoded_message = {
                'instrument': self.instrument_name,
                'function': func_name,
                'args': args,
                'kwargs': kwargs
            }
            self._send_message(json.dumps(unencoded_message))
            while True:
                if len(self.messages) > 0:
                    print('found messages')
                for message in self.messages:
                    print(message)
                    if message['function'] == func_name:
                        print('!', message)
                        return message['response']
    return RemoteInstrument


RemoteEPCDriver = remote_instrument(EPCDriver, 'epc')

if __name__ == '__main__':
    rd = RemoteEPCDriver(
        'https://king-prawn-app-yv9q2.ondigitalocean.app', 'bob', 'alice')
    rd.setDC()
