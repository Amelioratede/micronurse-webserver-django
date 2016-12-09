import os
import sys
from micronurse.settings import BASE_DIR


def register_test_account(sender, **kwargs):
    from micronurse_webserver.models import Account
    from micronurse_webserver.models import Guardianship
    from micronurse_webserver.models import Friendship

    test_older_account = Account.objects.filter(phone_number='123456')
    test_older_friend_account = Account.objects.filter(phone_number='233333')
    if not test_older_account or not test_older_friend_account:
        img_file = open(os.path.join(BASE_DIR, 'micronurse_webserver/default-portrait'), 'rb')
        img_bin = bytes(img_file.read())
        if not test_older_account:
            test_older_account = Account(user_id=100,
                                         phone_number='123456',
                                         password='123456',
                                         gender='M',
                                         account_type='O',
                                         nickname='Test-老人',
                                         portrait=img_bin)
            test_older_account.save()
            print('Test older account created.')
        else:
            test_older_account = test_older_account.get()

        if not test_older_friend_account:
            test_older_friend_account = Account(phone_number='233333',
                                                password='123456',
                                                gender='F',
                                                account_type='O',
                                                nickname='Test-老人好友',
                                                portrait=img_bin)
            test_older_friend_account.save()
            print('Test older friend account created.')
        else:
            test_older_friend_account = test_older_friend_account.get()

        friendship = Friendship(older=test_older_account, friend=test_older_friend_account)
        friendship.save()
        friendship = Friendship(older=test_older_friend_account, friend=test_older_account)
        friendship.save()
        print('Test older friendship created.')
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
        print('Test guardianship created.')


if sys.argv[1] == 'migrate':
    from django.db.models.signals import post_migrate

    post_migrate.connect(register_test_account)
elif sys.argv[1] == 'runserver':
    default_app_config = 'micronurse_webserver.apps.MicronurseWebserverConfig'
