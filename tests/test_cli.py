import os

from conftest import conf_matches_identity

def test_store_empty(cli_app):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    cli_app.send_input('save')
    out = cli_app.stdout._read()
    print(out)
    assert len(list(identity_store.values())) == 1
    identity = list(identity_store.values())[0]
    assert identity.access_key_id is None
    assert identity.secret_access_key is None

def test_add_command(cli_app, identity_fixures):
    from awsident.identity import Identity

    identity_store = cli_app.config_handler_fixtures['identity_store']
    data = identity_fixures[0]
    args = ['add']

    args.extend([data[key] for key in cli_app.add_command_steps])
    cli_app.send_input(*args)
    print(cli_app.stdout._read())

    identity = identity_store.get(data['access_key_id'])
    test_identity = Identity(**data)
    assert identity == test_identity

def test_edit_command(cli_app, identity_fixures):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    identity_store.add_identities(*identity_fixures)
    cli_app.send_input('edit', '1', '2', 'a_different_id')
    out = cli_app.stdout._read()
    print(out)
    identity = identity_store.get('a_different_id')
    assert identity is not None

def test_change_command(cli_app, identity_fixures):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    identity_store.add_identities(*identity_fixures)
    handler = cli_app.config_handler_fixtures['handler']
    def change_and_test(ident_index):
        key, name = cli_app.identities[i]
        identity = identity_store.get(key)
        assert identity is not None
        cli_app.send_input('change', str(i + 1))
        out = cli_app.stdout._read()
        print(out)
        assert conf_matches_identity(handler, identity)
    for i in range(3):
        change_and_test(i)
