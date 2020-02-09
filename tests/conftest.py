def pytest_configure():
    from django.conf import settings

    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        INSTALLED_APPS=(
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'rest_framework',
            'drf_nested_multipart'
        ),
    )

    try:
        import django
        django.setup()
    except AttributeError:
        pass
