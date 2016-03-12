import os
import string

import pytest

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
