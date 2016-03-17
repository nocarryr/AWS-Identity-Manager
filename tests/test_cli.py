import os

from conftest import conf_matches_identity

def test_store_empty(cli_app):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    cli_app.sendline('save')
    cli_app.expect('> ')

    identity_store.reload()
    assert len(list(identity_store.values())) == 1
    identity = list(identity_store.values())[0]
    assert identity.access_key_id is None
    assert identity.secret_access_key is None

def test_add_command(cli_app, identity_fixures):
    from awsident.identity import Identity

    identity_store = cli_app.config_handler_fixtures['identity_store']
    data = identity_fixures[0]
    cli_app.sendline('add')
    keys = ['name', 'access_key_id', 'secret_access_key']
    for key in keys:
        cli_app.expect(': ')
        cli_app.sendline(data[key])
    cli_app.expect('> ')

    identity_store.reload()
    identity = identity_store.get(data['access_key_id'])
    test_identity = Identity(**data)
    assert identity == test_identity

def test_edit_command(cli_app, identity_fixures):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    identity_store.add_identities(*identity_fixures)

    cli_app.sendline('reload')
    cli_app.expect('> ')

    cmds = ['edit', '1', '2', 'a_different_id']
    for i, cmd in enumerate(cmds):
        if i > 0:
            cli_app.expect(': ')
        cli_app.sendline(cmd)
    cli_app.expect('> ')

    identity_store.reload()
    identity = identity_store.get('a_different_id')
    assert identity is not None

def test_change_command(cli_app, identity_fixures):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    identity_store.add_identities(*identity_fixures)
    handler = cli_app.config_handler_fixtures['handler']

    cli_app.sendline('reload')
    cli_app.expect('> ')

    def change_and_test(ident_index):
        identity = list(identity_store.values())[i]
        cli_app.sendline('change')
        cli_app.expect(': ')
        cli_app.sendline(str(i + 1))
        cli_app.expect('> ')

        assert conf_matches_identity(handler, identity)
    for i in range(3):
        change_and_test(i)

def test_import_command(cli_app):
    identity_store = cli_app.config_handler_fixtures['identity_store']
    assert len(identity_store.identities) == 0
    cli_app.sendline('import tests/credentials.csv')
    cli_app.expect('> ')

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
    cli_app.send(os.linesep)
    cli_app.expect('> ')

    # user-expanded (~) completion
    rel_cwd = get_relative_cwd()
    print('relative cwd: {0}'.format(rel_cwd))
    rel_cwd = os.path.join('~', rel_cwd)
    cli_app.send('import {0}\ttest\tcredent\t'.format(rel_cwd))
    cli_app.expect('.csv')
    cli_app.send(os.linesep)
    cli_app.expect('> ')

    # absolute path completion
    cli_app.send('import {0}\ttest\tcredent\t'.format(os.getcwd()))
    cli_app.expect('.csv')
    cli_app.send(os.linesep)
    cli_app.expect('> ')
