import os

from conftest import conf_matches_identity

def test_store_empty(cli_app):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    cli_app.send_and_wait('save')

    identity_store.reload()
    assert len(list(identity_store.values())) == 1
    identity = list(identity_store.values())[0]
    assert identity.access_key_id is None
    assert identity.secret_access_key is None

def test_add_command(cli_app, identity_fixures):
    from awsident.identity import Identity

    identity_store = cli_app.config_handler_fixtures['identity_store']
    data = identity_fixures[0]

    prompt = ': '
    cli_app.send_and_wait('add', prompt)
    keys = cli_app.app_class.add_command_steps
    for i, key in enumerate(keys):
        if i == len(keys) - 1:
            prompt = None
        cli_app.send_and_wait(data[key], prompt)

    identity_store.reload()
    identity = identity_store.get(data['access_key_id'])
    test_identity = Identity(**data)
    assert identity == test_identity

def test_edit_command(cli_app, identity_fixures):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    identity_store.add_identities(*identity_fixures)

    cli_app.send_and_wait('reload')

    cmds = ['edit', '1', '2', 'a_different_id']
    prompt = ': '
    for i, cmd in enumerate(cmds):
        if i == len(cmds) - 1:
            prompt = None
        cli_app.send_and_wait(cmd, prompt)

    identity_store.reload()
    identity = identity_store.get('a_different_id')
    assert identity is not None

def test_change_command(cli_app, identity_fixures):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    identity_store.add_identities(*identity_fixures)
    handler = cli_app.config_handler_fixtures['handler']

    cli_app.send_and_wait('reload')

    def change_and_test(ident_index):
        identity = list(identity_store.values())[i]
        cli_app.send_and_wait('change', ': ')
        cli_app.send_and_wait(str(i + 1))
        assert conf_matches_identity(handler, identity)

    for i in range(3):
        change_and_test(i)

def test_import_command(cli_app):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    assert len(identity_store.identities) == 0
    cli_app.send_and_wait('import tests/credentials.csv')

    identity_store.reload()
    assert len(identity_store.identities) == 2

def test_import_completion(cli_app):
    def get_relative_cwd():
        home_dir = os.path.expanduser('~')
        p = ''
        head = os.getcwd()
        while not os.path.samefile(home_dir, head):
            head, tail = os.path.split(head)
            p = os.path.join(tail, p)
        return p

    # direct relative path completion
    cli_app.send('import test\tcredent\t')
    cli_app.expect('.csv')
    cli_app.send_and_wait('')

    # user-expanded (~) completion
    rel_cwd = get_relative_cwd()
    print('relative cwd: {0}'.format(rel_cwd))
    rel_cwd = os.path.join('~', rel_cwd)
    cli_app.send('import {0}\ttest\tcredent\t'.format(rel_cwd))
    cli_app.expect('.csv')
    cli_app.send_and_wait('')

    # absolute path completion
    cli_app.send('import {0}\ttest\tcredent\t'.format(os.getcwd()))
    cli_app.expect('.csv')
    cli_app.send_and_wait('')

def test_help(cli_app):
    for cmd in cli_app.app_class.doc_cmds:
        cli_app.send_and_wait('help {0}'.format(cmd))
