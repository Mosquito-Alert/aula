import app_config

from main.models import EducationCenter


def init_center_hashtags():
    centers = EducationCenter.objects.filter(hashtag__isnull=True)
    for c in centers:
        c.hashtag = c.center_slug()
        c.save()


def main():
    init_center_hashtags()


if __name__ == '__main__':
    main()
