import os
import json

import pytest

def test_add_single(identity_fixures, identity_store):
    for d in identity_fixures:
        identity = identity_store.add_identity(d)
        for key, val in d.items():
            assert getattr(identity, key) == val

def test_add_multiple(identity_fixures, identity_store):
    identity_store.add_identities(*identity_fixures)
    assert len(identity_store.identities) == len(identity_fixures)

def test_id_validation(identity_fixures, identity_store):
    from awsident.storage import IdentityExists

    identity_store.add_identities(*identity_fixures)
    with pytest.raises(IdentityExists):
        identity_store.add_identity(identity_fixures[0])
    identity = list(identity_store.values())[0]
    original_id = identity.id
    identity.access_key_id = 'ichanged'
    assert 'ichanged' in identity_store.keys()
    assert original_id not in identity_store.keys()

def test_serialization(identity_fixures, identity_store):
    identity_store.add_identities(*identity_fixures)
    # data should have been saved at this point so clear and reload it
    identity_store.identities.clear()
    identity_store.load_from_config()
    for data in identity_fixures:
        identity = identity_store.get(data['access_key_id'])
        for key, val in data.items():
            assert getattr(identity, key) == val
