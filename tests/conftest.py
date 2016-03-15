import sys
import os
import string
import threading
import collections
try:
    import ConfigParser as configparser
except ImportError:
    import configparser


import pytest

PY2 = sys.version_info.major == 2

def read_conf_file(handler_cls):
    assert os.path.exists(handler_cls.conf_filename)
    p = configparser.SafeConfigParser()
    p.read(handler_cls.conf_filename)
    d = {}
    for attr_key, option_name in handler_cls.attr_map.items():
        if handler_cls.section_name.lower() == 'default':
            val = p.defaults().get(option_name)
        else:
            val = p.get(handler_cls.section_name, option_name)
        d[attr_key] = val
    return d

def conf_matches_identity(handler_cls, identity):
    from awsident.identity import Identity

    if not isinstance(identity, Identity):
        identity = Identity(**identity)
    for cls in handler_cls.__subclasses__():
        d = read_conf_file(cls)
        for key in cls.attr_map.keys():
            if getattr(identity, key) != d[key]:
                return False
    return True

@pytest.fixture
def identity_fixures():
    l = []
    for i, c in enumerate(string.ascii_uppercase):
        l.append(dict(
            name='identity_{0}'.format(i),
            access_key_id='someaccesskey_{0}'.format(c),
            secret_access_key='notasecret_{0}_{1}'.format(i, c),
        ))
    return l

@pytest.fixture
def identity_store(tmpdir):
    from awsident.storage import IdentityStore
    identity_store = IdentityStore(config_path=str(tmpdir))
    return identity_store

@pytest.fixture
def identity_store_with_data(tmpdir):
    from awsident.storage import IdentityStore
    identity_store = IdentityStore(config_path=str(tmpdir))
    for data in identity_fixures():
        identity_store.add_identity(data)
    return identity_store

@pytest.fixture
def config_handler_fixtures(tmpdir, identity_store):
    from awsident import handlers

    handlers.identity_store = identity_store
    conf_files = {}
    for cls in handlers.ConfigHandler.__subclasses__():
        fn = os.path.expanduser(cls.conf_filename)
        p = tmpdir.join(fn)
        cls.conf_filename = str(p)
        conf_files[cls] = p
    return dict(
        handler=handlers.ConfigHandler,
        conf_files=conf_files,
        identity_store=identity_store,
    )


@pytest.fixture
def cli_app(config_handler_fixtures, monkeypatch):


    class FakeInput(object):
        def __init__(self):
            self.buffer = collections.deque()
            self.input_ready = threading.Event()
        def __call__(self, *args):
            self.input_ready.wait()
            s = self.buffer.popleft()
            if not len(self.buffer):
                self.input_ready.clear()
            return s
        def send_input(self, *args):
            print('fake_input: ', args)
            for arg in args:
                self.buffer.append(arg)
            self.input_ready.set()

    fake_input = FakeInput()

    if PY2:
        monkeypatch.setattr('__builtin__.raw_input', fake_input)
    else:
        monkeypatch.setattr('builtins.input', fake_input)

    import main
    main.identity_store = config_handler_fixtures['identity_store']

    class StdOut(object):
        def __init__(self):
            self.clear()
        def write(self, s):
            self.buffer += s
        def read(self):
            raise NotImplementedError
        def clear(self):
            self.buffer = ''
        def _read(self):
            s = self.buffer
            self.clear()
            return s

    class CliApp(main.Main):
        def send_input(self, *args):
            fake_input.send_input(*args)
            t = self.cli_thread
            t.postcmd.wait()
            t.postcmd.clear()
        def preloop(self):
            self.cli_thread.running.set()
        def postcmd(self, stop, line):
            t = self.cli_thread
            t.postcmd.set()
            return stop
        def pseudo_raw_input(self, prompt):
            t = self.cli_thread
            t.running.set()
            return main.Main.pseudo_raw_input(self, prompt)

    class CliThread(threading.Thread):
        def __init__(self):
            super(CliThread, self).__init__()
            self.running = threading.Event()
            self.stopped = threading.Event()
            self.postcmd = threading.Event()
        def run(self):
            app = self.cli_app = CliApp()
            app.stdout = StdOut()
            app.cli_thread = self
            app._cmdloop()
            self.running.clear()
            self.stopped.set()
        def stop(self):
            if self.stopped.is_set():
                return
            self.running.clear()
            self.postcmd.set()
            self.cli_app.send_input(*['exit', ';\n', 'EOF', '\x03', '\x04'])
            self.stopped.wait(5)
            if not self.stopped.is_set():
                print('cli hang.. exiting')
                sys.exit(1)

    cli_thread = CliThread()
    cli_thread.daemon = True
    cli_thread.start()
    cli_thread.running.wait()
    app = cli_thread.cli_app
    app.config_handler_fixtures = config_handler_fixtures

    def fin():
        cli_thread.stop()
    return app
