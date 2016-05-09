from django.db.models.signals import post_migrate


def register_test_account(sender, **kwargs):
    from micronurse_webserver.models import Account
    testAccount  = Account.objects.filter(phone_number='123456')
    if not testAccount:
        testAccount = Account(phone_number='123456',
                              password='123456',
                              gender='M',
                              nickname='Test')
        testAccount.save()
        print('Test account created.')

post_migrate.connect(register_test_account)
