from EPC04 import EPCDriver


class RemoteEPCDriver(EPCDriver):

    def __init__(self):
        methods = filter(self._is_public_method, dir(self))
        for method in methods:
            setattr(self, method, self._remote_decorator(getattr(self, method)))

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
        print(
            f'Calling function {func_name} with args {args} and kwargs {kwargs}')


if __name__ == '__main__':
    rd = RemoteEPCDriver()
    rd.setDC()
