import app_config

from main.models import EducationCenter


def main():
    for e in EducationCenter.objects.all():
        #if e.hashtag is None:
        e.hashtag = e.center_slug()
        e.save()


if __name__ == '__main__':
    main()
