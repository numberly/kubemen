from kubemen.connectors.email import Email


def test_send(app, change, character, user, mocker):
    email = Email(app.config, {})
    email.send(change, character, user)
