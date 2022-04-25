import os, sys

from airflow.models import BaseOperator


def setup_django_for_airflow():
    # Add Django project root to path
    sys.path.append('./project_root/')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")

    import django
    django.setup()


class DjangoOperator(BaseOperator):

    def pre_execute(self, *args, **kwargs):
        setup_django_for_airflow()