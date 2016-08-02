import os

from django.db.models.signals import post_migrate

from micronurse.settings import BASE_DIR


def register_test_account(sender, **kwargs):
    from micronurse_webserver.models import Account
    test_account = Account.objects.filter(phone_number='123456')
    if not test_account:
        img_file = open(os.path.join(BASE_DIR, 'micronurse_webserver/default-portrait'), 'rb')
        img_bin = bytes(img_file.read())
        test_account = Account(phone_number='123456',
                              password='123456',
                              gender='M',
                              account_type='O',
                              nickname='Test-老人',
                              portrait=img_bin)
        test_account.save()
        print('Test account created.')

post_migrate.connect(register_test_account)
