import os
import sys
from micronurse.settings import BASE_DIR


def register_test_account(sender, **kwargs):
    from micronurse_webserver.models import Account
    from micronurse_webserver.models import Guardianship
    test_older_account = Account.objects.filter(phone_number='123456')
    if not test_older_account:
        img_file = open(os.path.join(BASE_DIR, 'micronurse_webserver/default-portrait'), 'rb')
        img_bin = bytes(img_file.read())
        test_older_account = Account(phone_number='123456',
                                     password='123456',
                                     gender='M',
                                     account_type='O',
                                     nickname='Test-老人',
                                     portrait=img_bin)
        test_older_account.save()
        print('Test older account created.')
    else:
        test_older_account = test_older_account.get()

    test_guardian_account = Account.objects.filter(phone_number='666666')
    if not test_guardian_account:
        img_file = open(os.path.join(BASE_DIR, 'micronurse_webserver/default-portrait'), 'rb')
        img_bin = bytes(img_file.read())
        test_guardian_account = Account(phone_number='666666',
                                        password='123456',
                                        gender='F',
                                        account_type='G',
                                        nickname='Test-监护人',
                                        portrait=img_bin)
        test_guardian_account.save()
        print('Test guardian account created.')
        relation = Guardianship(older=test_older_account, guardian=test_guardian_account)
        relation.save()


if sys.argv[1] == 'migrate':
    from django.db.models.signals import post_migrate
    post_migrate.connect(register_test_account)
elif sys.argv[1] == 'runserver':
    default_app_config = 'micronurse_webserver.apps.MicronurseWebserverConfig'
