import os

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
