import sys
import os
import string
import threading

import pytest

collect_ignore = []
if sys.version_info.major == 3 and sys.version_info.minor == 5:
    collect_ignore.append('test_cli.py')

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
def cli_app(config_handler_fixtures):
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
        def send_input(self, s):
            t = self.cli_thread
            t.input_buffer = s
            t.input_ready.set()
            t.postcmd.wait()
            t.postcmd.clear()
        def preloop(self):
            self.cli_thread.running.set()
        def postcmd(self, stop, line):
            self.cli_thread.postcmd.set()
            return stop
        def pseudo_raw_input(self, prompt):
            t = self.cli_thread
            t.running.set()
            t.input_ready.wait()
            if isinstance(t.input_buffer, list):
                data = t.input_buffer[0]
                t.input_buffer = t.input_buffer[1:]
                if not len(t.input_buffer):
                    t.input_buffer = None
                    t.input_ready.clear()
            else:
                data = t.input_buffer
                t.input_ready.clear()
            return data

    class CliThread(threading.Thread):
        def __init__(self):
            super(CliThread, self).__init__()
            self.running = threading.Event()
            self.stopped = threading.Event()
            self.input_ready = threading.Event()
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
            self.cli_app.send_input('exit')
            self.stopped.wait()

    cli_thread = CliThread()
    cli_thread.daemon = True
    cli_thread.start()
    cli_thread.running.wait()
    app = cli_thread.cli_app
    app.config_handler_fixtures = config_handler_fixtures

    def fin():
        cli_thread.stop()
    return app
