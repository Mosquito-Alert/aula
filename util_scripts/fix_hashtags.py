import app_config

from main.models import Quiz, QuizRun, Campaign, QuizRunAnswers, Profile, EducationCenter
import os


def reset_hashtags():
    Profile.objects.filter(is_group=True).update(group_hashtag=None)
    for center in EducationCenter.objects.all():
        groups = center.center_groups()
        index = 1
        for group in groups:
            group.profile.group_hashtag = center.hashtag + "_" + str(index)
            group.profile.save()
            index = index + 1


def main():
    reset_hashtags()


if __name__ == '__main__':
    main()