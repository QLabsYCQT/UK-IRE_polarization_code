import json
from .server import MessageSender
import threading
from time import sleep
import pickle
import codecs


def remote_instrument(instrument, name):
    class RemoteInstrument(instrument):

        def __init__(self, hostname, local_name, remote_name, token):
            self.hostname = hostname
            self.local_name = local_name
            self.remote_name = remote_name
            self.messenger = MessageSender(self.local_name, self.hostname, token)
            self.messages = []
            methods = filter(self._is_public_method,
                             dir(self.instrument))
            attributes = filter(self._is_public_attribute,
                                dir(self.instrument))
            for method in methods:
                setattr(self,
                        method,
                        self._remote_decorator(getattr(self, method)))
            for attribute in attributes:
                setattr(self.__class__,
                        attribute,
                        property(
                            self._remote_getter(attribute),
                            self._remote_setter(attribute)
                        ))
            # Empty message buffer on server
            self.messenger.retrieve_messages()

        def _send_message(self, message):
            return self.messenger.send_message(self.remote_name, message)

        def _retrieve_messages(self):
            while True:
                new_messages = self.messenger.retrieve_messages()
                if len(new_messages) > 0:
                    self.messages += [json.loads(message) for message in new_messages]
                    break
                sleep(0.01)

        def _is_public_method(self, member):
            is_method = callable(getattr(self.instrument, member))
            is_public = member[0] != '_'
            return is_method & is_public

        def _is_public_attribute(self, member):
            is_method = callable(getattr(self.instrument, member))
            is_public = member[0] != '_'
            return (not is_method) & is_public

        def _remote_decorator(self, method):
            def wrapper(*args, **kwargs):
                resp = self._call_remote_method(method.__name__, args, kwargs)
                return resp
            return wrapper

        def _call_remote_method(self, method, args, kwargs):
            unencoded_message = {
                'instrument': self.instrument_name,
                'type': 'method',
                'method': method,
                'args': args,
                'kwargs': kwargs
            }
            self._send_message(json.dumps(unencoded_message))
            while True:
                if len(self.messages) > 0:
                    for message in self.messages:
                        if (message['type'] == 'method') & \
                                (message['method'] == method):
                            self.messages.remove(message)
                            return message['response']
                self._retrieve_messages()

        def _remote_getter(self, attribute):
            def _get_remote_attribute(self):
                unencoded_message = {
                    'instrument': self.instrument_name,
                    'action': 'get',
                    'type': 'attribute',
                    'attribute': attribute
                }
                self._send_message(json.dumps(unencoded_message))
                while True:
                    if len(self.messages) > 0:
                        for message in self.messages:
                            if (message['type'] == 'attribute') & \
                                ((message['attribute'] == attribute) & \
                                    (message['action'] == 'get')):
                                self.messages.remove(message)
                                assert message not in self.messages
                                return pickle.loads(
                                    codecs.decode(message['value'].encode(),
                                                'base64')
                                )
                    self._retrieve_messages()
            return _get_remote_attribute

        def _remote_setter(self, attribute):
            def _set_remote_attribute(self, value):
                unencoded_message = {
                    'instrument': self.instrument_name,
                    'action': 'set',
                    'type': 'attribute',
                    'attribute': attribute,
                    'value': codecs.encode(pickle.dumps(value),
                                           'base64').decode()
                }
                self._send_message(json.dumps(unencoded_message))
                while True:
                    if len(self.messages) > 0:
                        for message in self.messages:
                            if (message['type'] == 'attribute') & \
                                ((message['attribute'] == attribute) & \
                                    (message['action'] == 'set')):
                                self.messages.remove(message)
                                return None
                    self._retrieve_messages()
            return _set_remote_attribute

    remote_instrument = RemoteInstrument
    remote_instrument.instrument = instrument
    remote_instrument.instrument_name = name
    return remote_instrument
