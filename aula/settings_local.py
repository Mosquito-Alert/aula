from pathlib import Path

DEBUG = True

ALLOWED_HOSTS=['127.0.0.1',]

SECRET_KEY='*)fth+=#p1%e2vxiabf3bs0=)0(e^7rkh7wmp!lyd=vzhomntw'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
	    'ENGINE': 'django.contrib.gis.db.backends.postgis',
        #'NAME': 'aula_test',
        'NAME': 'aula',
        #'NAME': 'aula_campanya_octubre_2021',
        #'NAME': 'aula_merge_2022',
        #'NAME': 'aula_now',
        #'NAME': 'aula_prod',
        #'NAME': 'aula_estiu_2021',
        'USER': 'aula_user',
        'PASSWORD': 'F7PTxpp8_%_8=X#j9ZKQRnxCs+vaqv=EH^_y3QDBD7$je?tApxBNHa6NBEQ+&%ca',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
