from rest_framework import serializers
from main.models import EducationCenter, Quiz, Question, QuizRunAnswers, QuizRun, Campaign, BreedingSites, Awards
from django.contrib.auth.models import User
from django.urls import reverse

class EducationCenterSerializer(serializers.ModelSerializer):
    pos_x = serializers.SerializerMethodField()
    pos_y = serializers.SerializerMethodField()

    class Meta:
        model = EducationCenter
        fields = '__all__'

    def get_pos_x(self, obj):
        geom = obj.location
        if geom is None:
            return None
        else:
            return geom.y

    def get_pos_y(self, obj):
        geom = obj.location
        if geom is None:
            return None
        else:
            return geom.x


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class NestedQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id','name']


class QuizSerializer(serializers.ModelSerializer):

    education_center = serializers.SerializerMethodField('get_quiz_center')
    author = ShortUserSerializer()
    requisite = NestedQuizSerializer()
    quiz_start_url = serializers.SerializerMethodField('get_start_url')
    type_text = serializers.SerializerMethodField('get_type_text')
    seq = serializers.SerializerMethodField('get_seq')

    class Meta:
        model = Quiz
        fields = '__all__'

    def get_seq(self,obj):
        return obj.seq

    def get_quiz_center(self,obj):
        if obj.author and obj.author.profile and obj.author.profile.is_teacher:
            return obj.author.profile.teacher_belongs_to.name
        return None

    def get_start_url(self,obj):
        if obj.type == 3:
            return reverse('quiz_upload_link', kwargs={'quiz_id':obj.id})
        else:
            return reverse('quiz_take_splash', kwargs={'pk':obj.id})

    def get_type_text(self, obj):
        return obj.type_text


class AlumSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField('get_teacher')
    groups = serializers.SerializerMethodField('get_groups')

    class Meta:
        model = User
        fields = '__all__'

    def get_teacher(self,obj):
        if obj.profile and obj.profile.alum_teacher:
            return obj.profile.alum_teacher.username
        else:
            return ''

    def get_groups(self, obj):
        return obj.profile.groups_string


class GroupSearchSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField('get_text')
    class Meta:
        model = User
        fields = ['id','text']

    def get_text(self, obj):
        return obj.profile.group_public_name


class QuizSearchSerializer(serializers.ModelSerializer):

    text = serializers.SerializerMethodField('get_text')

    class Meta:
        model = Quiz
        fields = ['id', 'text']

    def get_text(self, obj):
        return obj.name


class AlumSearchSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField('get_text')
    class Meta:
        model = User
        fields = ['id','text']

    def get_text(self, obj):
        return obj.username


class GroupSerializer(serializers.ModelSerializer):
    group_password = serializers.SerializerMethodField('get_group_password')
    group_public_name = serializers.SerializerMethodField('get_group_public_name')
    group_center = serializers.SerializerMethodField('get_group_center')
    group_class = serializers.SerializerMethodField('get_group_class')
    #group_alums = serializers.SerializerMethodField('get_group_alums')
    group_picture = serializers.SerializerMethodField('get_group_picture')
    group_tutor = serializers.SerializerMethodField('get_group_tutor')
    group_n_students = serializers.SerializerMethodField('get_group_n_students')
    group_hashtag = serializers.SerializerMethodField('get_group_hashtag')

    class Meta:
        model = User
        fields = '__all__'

    def get_group_class(self,obj):
        return obj.profile.group_class

    def get_group_hashtag(self,obj):
        return obj.profile.group_hashtag

    def get_group_n_students(self,obj):
        return obj.profile.n_students_in_group

    def get_group_password(self,obj):
        return obj.profile.group_password

    def get_group_public_name(self, obj):
        return obj.profile.group_public_name

    def get_group_center(self,obj):
        if obj.profile is not None:
            return obj.profile.center_string
        return ''

    def get_group_tutor(self, obj):
        tutor = obj.profile.group_teacher
        if tutor is not None:
            return tutor.username
        return ''

    # def get_group_alums(self,obj):
    #     alums = []
    #     for alum in obj.alum_groups.all():
    #         alums.append(alum.user.username)
    #     return ','.join(alums)

    def get_group_picture(self,obj):
        if obj.profile:
            if obj.profile.group_picture:
                #return obj.profile.group_picture.url
                try:
                    return obj.profile.group_picture_thumbnail.url
                except ValueError:
                    return obj.profile.group_picture.url
        return ''


class QuizComboSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'name']

class GroupComboSerializer(serializers.ModelSerializer):
    public_name = serializers.SerializerMethodField('get_public_name')

    class Meta:
        model = User
        fields = ['id','username','public_name']

    def get_public_name(self,obj):
        if obj.profile:
            return obj.profile.group_public_name
        else:
            return ''

class TeacherComboSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']


class TeacherSerializer(serializers.ModelSerializer):
    center = serializers.SerializerMethodField('get_center')
    password = serializers.SerializerMethodField('get_password')

    class Meta:
        model = User
        fields = ['id','username','center','is_active','password']

    def get_center(self,obj):
        if obj.profile:
            return obj.profile.teacher_belongs_to.name
        else:
            return ''

    def get_password(self,obj):
        if obj.profile:
            return obj.profile.teacher_password
        else:
            return ''


class QuizRunAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizRunAnswers
        fields = '__all__'


class QuizRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizRun
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


class BreedingSiteSerializer(serializers.ModelSerializer):
    observation_date = serializers.SerializerMethodField('get_observation_date')

    class Meta:
        model = BreedingSites
        fields = '__all__'

    def get_observation_date(self,obj):
        return obj.observation_date.strftime("%d/%m/%Y")


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Awards
        fields = '__all__'
