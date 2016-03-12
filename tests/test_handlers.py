import os
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import pytest

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

def test_identity_change(config_handler_fixtures, identity_fixures):
    handler = config_handler_fixtures['handler']
    identity_store = config_handler_fixtures['identity_store']
    identity_store.add_identities(*identity_fixures)
    identity = list(identity_store.values())[0]
    handler.change_identity(identity)
    for cls in handler.__subclasses__():
        d = read_conf_file(cls)
        for key in cls.attr_map.keys():
            assert getattr(identity, key) == d[key]

def test_identity_save(config_handler_fixtures, identity_fixures):
    from awsident.storage import IdentityExists

    handler = config_handler_fixtures['handler']
    identity_store = config_handler_fixtures['identity_store']
    identity_store.add_identities(*identity_fixures)
    identity = list(identity_store.values())[0]
    handler.change_identity(identity)
    with pytest.raises(IdentityExists):
        handler.save_identity()
    del identity_store.identities[identity.id]
    new_identity = handler.save_identity()
    for key in handler.attr_map.keys():
        assert getattr(new_identity, key) == getattr(identity, key)
