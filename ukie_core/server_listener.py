from .server import MessageSender
import threading
import json
from time import sleep
import pickle
import codecs


class ServerListener():

    def __init__(self, hostname, local_name, remote_name):
        self.hostname = hostname
        self.local_name = local_name
        self.remote_name = remote_name
        self.instruments = {}
        self.messenger = MessageSender(self.local_name, self.hostname)
        self.messenger.retrieve_messages()
        self.retrieve_thread = threading.Thread(
            name='retrieve',
            target=self._retrieve_messages,
            daemon=True)
        self.retrieve_thread.start()

    def _send_message(self, message):
        return self.messenger.send_message(self.remote_name, message)

    def _retrieve_messages(self):
        global stop_thread 
        stop_thread = False
        self.stop_thread = stop_thread
        while (not self.stop_thread):
            messages = [json.loads(message)
                        for message in self.messenger.retrieve_messages()]
            for message in messages:
                self.execute_message(message)
                del message
            sleep(0.01)

    def execute_message(self, message: dict):
        if message['type'] == 'method':
            self.execute_method(message)
        elif message['type'] == 'attribute':
            if message['action'] == 'get':
                self.get_attribute(message)
            elif message['action'] == 'set':
                self.set_attribute(message)

    def execute_method(self, message):
        instrument_name = message['instrument']
        method_name = message['method']
        args = message['args']
        kwargs = message['kwargs']
        instrument = self.instruments[instrument_name]
        method = getattr(instrument, method_name)

        reply = {
            'instrument': instrument_name,
            'type': 'method',
            'method': method_name,
            'response': method(*args, **kwargs)
        }
        self._send_message(json.dumps(reply))

    def get_attribute(self, message: dict):
        instrument_name = message['instrument']
        attribute_name = message['attribute']
        instrument = self.instruments[instrument_name]
        value = getattr(instrument, attribute_name)

        reply = {
            'instrument': instrument_name,
            'type': 'attribute',
            'action': 'get',
            'attribute': attribute_name,
            'value': codecs.encode(pickle.dumps(value), 'base64').decode()
        }
        self._send_message(json.dumps(reply))

    def set_attribute(self, message: dict):
        instrument_name = message['instrument']
        attribute_name = message['attribute']
        value = pickle.loads(codecs.decode(
            message['value'].encode(), 'base64'))
        instrument = self.instruments[instrument_name]
        setattr(instrument, attribute_name, value)

        reply = {
            'instrument': instrument_name,
            'type': 'attribute',
            'action': 'set',
            'attribute': attribute_name
        }
        self._send_message(json.dumps(reply))


