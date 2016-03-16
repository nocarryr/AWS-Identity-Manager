import sys
import os
import string
import json
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import pexpect
import pytest

PY2 = sys.version_info.major == 2

def read_conf_file(handler_cls):
    fn = handler_cls().full_conf_filename
    assert os.path.exists(fn)
    p = configparser.SafeConfigParser()
    p.read(fn)
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
def config_handler_fixtures(tmpdir):
    from awsident.storage import identity_store
    from awsident.handlers import ConfigHandler

    config_path = tmpdir.mkdir('aws-identity-manager')
    identity_store.config_path = str(config_path)

    ConfigHandler.conf_root = str(tmpdir)
    ConfigHandler.handler_config_path = str(config_path)
    return dict(
        handler=ConfigHandler,
        identity_store=identity_store,
    )

@pytest.fixture
def cli_app(config_handler_fixtures):
    identity_store = config_handler_fixtures['identity_store']
    handler = config_handler_fixtures['handler']
    conf_path = identity_store.config_path
    handler_conf = {'Global':{'conf_root':handler.conf_root}}
    with open(os.path.join(conf_path, 'handlers.json'), 'w') as f:
        f.write(json.dumps(handler_conf))
    lf = open('pexpect.log', 'wb')
    app = pexpect.spawn('python main.py --pytest-mode -c {0}'.format(conf_path), logfile=lf)
    app.config_handler_fixtures = config_handler_fixtures
    app.expect('> ')
    def fin():
        lf.close()
    return app
