import pytest

from conftest import conf_matches_identity

def test_identity_change(config_handler_fixtures, identity_fixures):
    handler = config_handler_fixtures['handler']
    identity_store = config_handler_fixtures['identity_store']
    identity_store.add_identities(*identity_fixures)
    identity = list(identity_store.values())[0]
    handler.change_identity(identity)
    assert conf_matches_identity(handler, identity)

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
    for key in list(handler.attr_map.keys()):
        assert getattr(new_identity, key) == getattr(identity, key)
