from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from main.forms import QuizForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from aula import settings
from main.models import EducationCenter, Word, Quiz, Answer, Question, QuizRun, QuizRunAnswers, Profile, get_string_from_groups, Campaign, QuizCorrection
from main.forms import TeacherForm, SimplifiedTeacherForm, EducationCenterForm, TeacherUpdateForm, ChangePasswordForm, \
    SimplifiedAlumForm, SimplifiedGroupForm, AlumUpdateForm, QuestionForm, QuestionLinkForm, SimplifiedAlumFormForTeacher, \
    SimplifiedAlumFormForAdmin, AlumUpdateFormAdmin, QuizAdminForm, QuestionPollForm, QuizNewForm, QuestionUploadForm, CampaignForm, \
    BreedingSites, Awards, QuestionOpenForm, OpenAnswerNewCorrectForm
from django.contrib.gis.geos import GEOSGeometry
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from querystring_parser import parser
import json
import functools
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import operator
from main.serializers import EducationCenterSerializer, TeacherSerializer, UserSerializer, AlumSerializer, \
    GroupSerializer, GroupSearchSerializer, TeacherComboSerializer, AlumSearchSerializer, QuizSerializer, \
    QuestionSerializer, QuizSearchSerializer, QuizRunAnswerSerializer, QuizRunSerializer, QuizComboSerializer, \
    GroupComboSerializer, CampaignSerializer, BreedingSiteSerializer, AwardSerializer
from rest_framework import status,viewsets, generics
from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse
from random import randint
from django.http import JsonResponse
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.core.files import File
from shutil import copy
import os
from django.contrib.auth.decorators import user_passes_test
from rest_framework.exceptions import ParseError
from datetime import datetime
import pytz
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from rest_framework import permissions
import uuid
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
import logging
from django.db import connection
from itertools import groupby
from django.db.models import Count

def get_order_clause(params_dict, translation_dict=None):
    order_clause = []
    try:
        order = params_dict['order']
        if len(order) > 0:
            for key in order:
                sort_dict = order[key]
                column_index_str = sort_dict['column']
                if translation_dict:
                    column_name = translation_dict[params_dict['columns'][int(column_index_str)]['data']]
                else:
                    column_name = params_dict['columns'][int(column_index_str)]['data']
                direction = sort_dict['dir']
                if direction != 'asc':
                    order_clause.append('-' + column_name)
                else:
                    order_clause.append(column_name)
    except KeyError:
        pass
    return order_clause


def get_filter_clause(params_dict, fields, translation_dict=None):
    filter_clause = []
    try:
        q = params_dict['search']['value']
        if q != '':
            for field in fields:
                if translation_dict:
                    translated_field_name = translation_dict[field]
                    filter_clause.append( Q(**{translated_field_name+'__icontains':q}) )
                else:
                    filter_clause.append(Q(**{field + '__icontains': q}))
    except KeyError:
        pass
    return filter_clause


def generic_datatable_list_endpoint(request,search_field_list,queryset, classSerializer, field_translation_dict=None, order_translation_dict=None, paginate=True):
    draw = -1
    start = 0
    try:
        draw = request.GET['draw']
    except:
        pass
    try:
        start = request.GET['start']
    except:
        pass
    #length = request.query_params.get('length', 25)
    length = 25

    get_dict = parser.parse(request.GET.urlencode())

    order_clause = get_order_clause(get_dict, order_translation_dict)

    filter_clause = get_filter_clause(get_dict, search_field_list, field_translation_dict)

    if len(filter_clause) == 0:
        queryset = queryset.order_by(*order_clause)
    else:
        queryset = queryset.order_by(*order_clause).filter(functools.reduce(operator.or_, filter_clause))

    if paginate:
        paginator = Paginator(queryset, length)

        recordsTotal = queryset.count()
        recordsFiltered = recordsTotal
        page = int(start) / int(length) + 1

        serializer = classSerializer(paginator.page(page), many=True)
    else:
        serializer = classSerializer(queryset, many=True, context={'request': request})
        recordsTotal = queryset.count()
        recordsFiltered = recordsTotal

    return Response({'draw': draw, 'recordsTotal': recordsTotal, 'recordsFiltered': recordsFiltered, 'data': serializer.data})


def is_teacher_test(user):
    if user.is_superuser:
        return True
    if user.profile and user.profile.is_teacher:
        return True
    return False


def is_alum_test(user):
    if user.is_superuser:
        return True
    if user.profile and user.profile.is_alum:
        return True
    return False


def is_group_test(user):
    if user.is_superuser:
        return True
    if user.profile and user.profile.is_group:
        return True
    return False

def page_not_found_view(request):
    return render(request, 'main/404.html', {})


def index(request):
    return render(request, 'main/index.html', {})


def credits(request):
    return render(request, 'main/credits.html', {})

@login_required
def my_hub(request):
    this_user = request.user
    if this_user.is_superuser:
        response = redirect('/admin_menu')
        return response
    if is_teacher_test(this_user):
        response = redirect('/teacher_menu')
        return response
    if is_alum_test(this_user):
        response = redirect('/group_menu')
        return response
    if is_group_test(this_user):
        response = redirect('/group_menu')
        return response

@login_required
def teacher_menu(request):
    if is_teacher_test(request.user):
        return render(request, 'main/teacher_menu.html', {})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "group_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})


@login_required
def admin_menu(request):
    if request.user.is_superuser:
        return render(request, 'main/admin_menu.html', {})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        if request.user.profile.is_alum:
            go_back_to = "group_menu"
        elif request.user.profile.is_teacher:
            go_back_to = "teacher_menu"
        else:
            go_back_to = "index"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

'''
@login_required
def group_menu(request):
    this_user = request.user
    teach = this_user.profile.alum_teacher
    quizzes_in_progress_ids = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=True).values('quiz__id').distinct()
    quizzes_done_ids = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).values('quiz__id').distinct()
    available_quizzes = Quiz.objects.filter(author=teach).filter(published=True).exclude(id__in=quizzes_in_progress_ids).exclude(id__in=quizzes_done_ids).order_by('id')
    in_progress_quizruns = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=True).order_by('-date')
    done_quizruns = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).order_by('-date')
    #in_progress_quizzes = Quiz.objects.filter(id__in=quizzes_in_progress_ids).order_by('id')
    #done_quizzes = Quiz.objects.filter(id__in=quizzes_done_ids).order_by('id')
    return render(request, 'main/alum_hub.html', {'available_quizzes':available_quizzes, 'in_progress_quizruns':in_progress_quizruns, 'done_quizruns': done_quizruns})
'''


@login_required
def teacher_polls(request):
    this_user = request.user
    if is_teacher_test(this_user):
        # filter(type=2).filter(professor_poll=True).
        teacher_campaign = this_user.profile.campaign
        all_quizzes_ordered = get_ordered_quiz_sequence(this_user)
        polls_in_progress_ids = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=True).values('quiz__id').distinct()
        polls_done_ids = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).values('quiz__id').distinct()
        available_polls = Quiz.objects.filter(campaign=teacher_campaign).filter(type=4).filter(author__isnull=True).filter(published=True).exclude(id__in=polls_in_progress_ids).exclude(id__in=polls_done_ids).order_by('id')
        in_progress_polls = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=True).order_by('-date')
        done_polls = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).order_by('-date')
        done_poll_ids = [a.quiz.id for a in done_polls]
        context = {
            'available_quizzes':available_polls,
            'in_progress_quizruns':in_progress_polls,
            'done_quizruns': done_polls,
            'done_quizzes_ids': done_poll_ids,
            'all_quizzes_ordered': all_quizzes_ordered,
            'teacher_campaign': teacher_campaign
        }
        return render(request, 'main/teacher_polls.html', context)
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "index"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})


def quiz_is_repeatable_for_user(quiz, this_user):
    if quiz.type == 5:
        return False
    elif quiz.type == 2:
        if this_user.profile.is_group:
            n_completed_quizruns_for_test = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).count()
            if n_completed_quizruns_for_test >= this_user.profile.n_students_in_group:
                return False
    elif quiz.type == 4:
        n_completed_quizruns_for_test = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).count()
        if n_completed_quizruns_for_test > 0:
            return False
    return True


def get_ordered_quiz_sequence(this_user):
    this_user_campaign = this_user.profile.campaign
    teach = None
    if this_user.profile.is_group:
        teach = this_user.profile.group_teacher
        all_quizzes_ordered = Quiz.objects.filter(Q(author=teach) | Q(author__isnull=True)).filter(published=True).filter(campaign=this_user_campaign).exclude(type=4).order_by('seq')
    else: #is teacher
        all_quizzes_ordered = Quiz.objects.filter(author__isnull=True).filter(published=True).filter(campaign=this_user_campaign).filter(type=4).order_by('seq')
    quizzes_in_progress_ids = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=True).values('quiz__id').distinct()
    in_progress = [ q['quiz__id'] for q in quizzes_in_progress_ids ]
    quizzes_done_ids = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).values('quiz__id').distinct()
    done = [ q['quiz__id'] for q in quizzes_done_ids ]
    if this_user.profile.is_group:
        available_quizzes = Quiz.objects.filter(Q(author=teach) | Q(author__isnull=True)).filter(published=True).filter(campaign=this_user_campaign).exclude(type=4).exclude(id__in=quizzes_in_progress_ids).exclude(id__in=quizzes_done_ids).order_by('id')
    else:
        available_quizzes = Quiz.objects.filter(Q(author=teach) | Q(author__isnull=True)).filter(published=True).filter(campaign=this_user_campaign).filter(type=4).exclude(id__in=quizzes_in_progress_ids).exclude(id__in=quizzes_done_ids).order_by('id')
    available_ids =  [ q.id for q in available_quizzes ]
    ordered_quizzes = []
    for quiz in all_quizzes_ordered:
        # quiz_status - locked/startable/repeatable/in_progress/done
        if quiz.requisite and not quiz.requisite.id in done:
            ordered_quizzes.append( {'quiz': quiz, 'status': 'blocked', 'blocked_by' : quiz.requisite})
        else:
            if quiz.id in available_ids:
                ordered_quizzes.append( { 'quiz': quiz, 'status': 'available', 'repeatable': quiz_is_repeatable_for_user(quiz,this_user) })
            elif quiz.id in in_progress:
                in_progress_quizrun = QuizRun.objects.get(taken_by=this_user, date_finished__isnull=True, quiz=quiz)
                ordered_quizzes.append({'quiz': quiz, 'status': 'in_progress', 'repeatable': False, 'quizrun':in_progress_quizrun })
            elif quiz.id in done:
                if quiz.is_upload:
                    done_upload = QuizRun.objects.get(taken_by=this_user, date_finished__isnull=False, quiz=quiz)
                    ordered_quizzes.append({'quiz': quiz, 'status': 'done', 'repeatable': False, 'file_url': done_upload.uploaded_file.url})
                elif quiz.is_open:
                    done_quizrun = QuizRun.objects.get(taken_by=this_user, date_finished__isnull=False, quiz=quiz)
                    corrected = QuizCorrection.objects.filter(corrected_quizrun=done_quizrun).filter(date_finished__isnull=False)
                    is_corrected = corrected.exists()
                    if is_corrected:
                        the_correction = corrected.first()
                    else:
                        the_correction = None
                    ordered_quizzes.append({'quiz': quiz, 'status': 'done', 'repeatable': False, 'is_corrected': is_corrected, 'correction': the_correction})
                else:
                    ordered_quizzes.append({'quiz': quiz, 'status': 'done', 'repeatable': quiz_is_repeatable_for_user(quiz,this_user)})
    return ordered_quizzes


@login_required
def group_menu(request):
    this_user = request.user
    this_user_campaign = this_user.profile.campaign
    teach = this_user.profile.group_teacher
    all_quizzes_ordered = get_ordered_quiz_sequence(this_user)
    quizzes_in_progress_ids = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=True).values('quiz__id').distinct()
    quizzes_done_ids = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).values('quiz__id').distinct()
    available_quizzes = Quiz.objects.filter(Q(author=teach) | Q(author__isnull=True)).filter(published=True).filter(campaign=this_user_campaign).exclude(type=4).exclude(id__in=quizzes_in_progress_ids).exclude(id__in=quizzes_done_ids).order_by('id')
    in_progress_quizruns = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=True).order_by('-date')
    done_quizruns = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).order_by('-date')
    done_quizzes_ids = [ a.quiz.id for a in done_quizruns ]

    done_test_ids = QuizRun.objects.filter(taken_by=this_user).filter(quiz__type=0).filter(date_finished__isnull=False).values('quiz__id').distinct()
    done_tests = Quiz.objects.filter(id__in=done_test_ids)
    done_test_scores = []
    for d in done_tests:
        done_test_scores.append({'id': d.id, 'best_run': d.best_run(this_user.id) })
    #in_progress_quizzes = Quiz.objects.filter(id__in=quizzes_in_progress_ids).order_by('id')
    #done_quizzes = Quiz.objects.filter(id__in=quizzes_done_ids).order_by('id')
    return render(request, 'main/alum_hub.html',
                  {
                      'available_quizzes':available_quizzes,
                      'in_progress_quizruns':in_progress_quizruns,
                      'done_quizruns': done_quizruns,
                      'done_quizzes_ids': done_quizzes_ids,
                      'all_quizzes_ordered': all_quizzes_ordered,
                      'done_test_scores': done_test_scores,
                      'campaign': this_user_campaign
                  })


@login_required
def quiz_new(request):
    this_user = request.user
    if this_user.is_superuser:
        if request.method == 'POST':
            form = QuizAdminForm(request.POST)
            if form.is_valid():
                pre_quiz = form.save(commit=False)
                id_requisite = request.POST.get('requisite', '')
                if id_requisite != -1 and id_requisite != '':
                    req = Quiz.objects.get(pk=int(id_requisite))
                    pre_quiz.requisite = req
                pre_quiz.save()
                return HttpResponseRedirect('/quiz/update/' + str(pre_quiz.id) + '/')
        else:
            form = QuizAdminForm()
        return render(request, 'main/quiz_new.html', {'form': form})
    elif this_user.profile and this_user.profile.is_teacher:
        if request.method == 'POST':
            form = QuizNewForm(request.POST, userid=this_user.id)
            if form.is_valid():
                pre_quiz = form.save(commit=False)
                pre_quiz.author = this_user
                pre_quiz.save()
                return HttpResponseRedirect('/quiz/update/' + str(pre_quiz.id) + '/')
        else:
            form = QuizNewForm(userid=this_user.id)
        return render(request, 'main/quiz_new_teacher.html', {'form': form})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})


@login_required
def question_open_new(request, quiz_id=None):
    quiz = None
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    else:
        raise forms.ValidationError("No existeix aquesta prova")
    if request.method == 'POST':
        form = QuestionOpenForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            return HttpResponseRedirect('/quiz/update/' + str(quiz_id) + '/')
    else:
        form = QuestionOpenForm()
    return render(request, 'main/question_open_new.html', {'form': form, 'quiz': quiz})


@login_required
def question_poll_new(request, quiz_id=None):
    quiz = None
    json_answers = None
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    else:
        raise forms.ValidationError("No existeix aquesta prova")
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        json_answers = request.POST.get('answers_json', '')
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            if json_answers != '':
                answers_data = json.loads(json_answers)
                for a in answers_data:
                    new_answer = Answer(
                        question=question,
                        label=a['label'],
                        text=a['text'],
                        is_correct=a['is_correct']
                    )
                    new_answer.save()
            return HttpResponseRedirect('/quiz/update/' + str(quiz_id) + '/')
    else:
        form = QuestionForm()
    return render(request, 'main/question_poll_new.html', {'form': form, 'quiz': quiz, 'json_answers': json_answers})


@login_required
def question_upload_new(request, quiz_id=None):
    quiz = None
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    else:
        raise forms.ValidationError("No existeix aquesta prova")
    if request.method == 'POST':
        form = QuestionUploadForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            return HttpResponseRedirect('/quiz/update/' + str(quiz_id) + '/')
    else:
        form = QuestionUploadForm()
    return render(request, 'main/question_upload_new.html', {'form': form, 'quiz': quiz })


@login_required
def question_link_new(request, quiz_id=None):
    quiz = None
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    else:
        raise forms.ValidationError("No existeix aquesta prova")
    if request.method == 'POST':
        form = QuestionLinkForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            return HttpResponseRedirect('/quiz/update/' + str(quiz_id) + '/')
    else:
        form = QuestionLinkForm()
    return render(request, 'main/question_link_new.html', {'form': form, 'quiz': quiz })


@login_required
def quiz_take_endsummary(request, quizrun_id=None):
    quizrun = None
    bestrun = None
    n_runs = 0
    if quizrun_id:
        quizrun = get_object_or_404(QuizRun, pk=quizrun_id)
        n_runs = quizrun.n_runs
        past_runs = n_runs - 1
    else:
        message = _("Sembla que aquesta prova no existeix.")
        go_back_to = "group_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    if not quizrun.is_done:
        message = _("Sembla que aquesta prova no està completada.")
        go_back_to = "group_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    return render(request, 'main/quiz_take_endsummary.html', {'quizrun': quizrun, 'n_runs': n_runs, 'past_runs': past_runs})


@login_required
def quiz_assign_admin(request):
    centers = EducationCenter.objects.all().order_by('name')
    return render(request, 'main/quiz_assign_admin.html', {'centers':centers})


@login_required
def poll_result_group(request, quiz_id=None, group_id=None):
    this_user = request.user
    quiz = None
    group = get_object_or_404(User, pk=group_id)
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    else:
        message = _("No existeix aquesta prova.")
        go_back_to = "quiz_results"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    if not QuizRun.objects.filter(quiz=quiz).exists():
        message = _("El test seleccionat no l'ha realitzat cap grup i encara no té resultats.")
        go_back_to = "quiz_results"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

    return render(request, 'main/poll_result_group.html', {'quiz': quiz, 'group': group})


@login_required
def poll_result(request, quiz_id=None):
    this_user = request.user
    quiz = None
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    else:
        message = _("No existeix aquesta prova.")
        go_back_to = "quiz_results"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    if not QuizRun.objects.filter(quiz=quiz).exists():
        message = _("El test seleccionat no l'ha realitzat cap grup i encara no té resultats.")
        go_back_to = "quiz_results"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

    return render(request, 'main/poll_result.html', {'quiz': quiz})

@login_required
def quiz_browse(request, quiz_id=None):
    this_user = request.user
    quiz = None
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    else:
        message = _("No existeix aquesta prova.")
        go_back_to = "group_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    if this_user.is_superuser:
        return render(request, 'main/quiz_browse.html', {'quiz': quiz})
    if not QuizRun.objects.filter(quiz=quiz).exists():
        message = _("No tens assignada aquesta prova, de manera que no la pots visualitzar.")
        go_back_to = "group_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

    return render(request, 'main/quiz_browse.html', {'quiz': quiz})

@login_required
def question_new(request, quiz_id=None):
    quiz = None
    json_answers = None
    question_picture = ''
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    else:
        raise forms.ValidationError("No existeix aquesta prova")
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if request.POST.get('question_picture'):
            question_picture = request.POST.get('question_picture')
        else:
            question_picture = ''
        json_answers = request.POST.get('answers_json','')
        if form.is_valid():
            question = form.save(commit=False)

            if question_picture != '':
                copy(str(settings.BASE_DIR) + question_picture, settings.MEDIA_ROOT + "/question_pics/")
                question.question_picture = '/question_pics/' + os.path.basename(question_picture)
            elif question_picture == '':
                question.question_picture = None

            question.quiz = quiz
            question.save()
            if json_answers != '':
                answers_data = json.loads(json_answers)
                for a in answers_data:
                    new_answer = Answer(
                        question=question,
                        label=a['label'],
                        text=a['text'],
                        is_correct=a['is_correct'],
                    )
                    new_answer.save()
            return HttpResponseRedirect('/quiz/update/' + str(quiz_id) + '/')
    else:
        form = QuestionForm()
    return render(request, 'main/question_new.html', {'form': form, 'quiz': quiz, 'json_answers': json_answers})

@login_required
def question_open_update(request, pk=None):
    question = None
    if pk:
        question = get_object_or_404(Question, pk=pk)
    form = QuestionOpenForm(request.POST or None, instance=question)
    if request.POST:
        if form.is_valid():
            question = form.save()
            return HttpResponseRedirect('/quiz/update/' + str(question.quiz.id) + '/')
    return render(request, 'main/question_open_edit.html',
                  {'form': form, 'question': question})

@login_required
def question_link_update(request, pk=None):
    question = None
    if pk:
        question = get_object_or_404(Question, pk=pk)
    form = QuestionLinkForm(request.POST or None, instance=question)
    if request.POST:
        if form.is_valid():
            question = form.save()
            return HttpResponseRedirect('/quiz/update/' + str(question.quiz.id) + '/')
    return render(request, 'main/question_link_edit.html',
                  { 'form': form, 'question': question })


@login_required
def question_upload_update(request, pk=None):
    question = None
    if pk:
        question = get_object_or_404(Question, pk=pk)
    form = QuestionUploadForm(request.POST or None, instance=question)
    if request.POST:
        if form.is_valid():
            question = form.save()
            return HttpResponseRedirect('/quiz/update/' + str(question.quiz.id) + '/')
    return render(request, 'main/question_upload_edit.html',{'form': form, 'question': question})


@login_required
def question_poll_update(request, pk=None):
    question = None
    if pk:
        question = get_object_or_404(Question, pk=pk)
        answers = question.sorted_answers_set
        json_answers = json.dumps([{'id': a.id, 'label': a.label, 'text': a.text, 'is_correct': a.is_correct} for a in answers])
    form = QuestionForm(request.POST or None, instance=question)
    if request.POST:
        json_answers = request.POST.get('answers_json', '')
        if form.is_valid():
            question = form.save(commit=False)
            question.answers.all().delete()
            question.save()
            answers_obj = json.loads(json_answers)
            for a in answers_obj:
                new_answer = Answer(
                    question=question,
                    label=a['label'],
                    text=a['text'],
                    is_correct=a['is_correct']
                )
                new_answer.save()
            return HttpResponseRedirect('/quiz/update/' + str(question.quiz.id) + '/')
    return render(request, 'main/question_poll_edit.html', {'form': form, 'question': question, 'json_answers': json_answers})


@login_required
def question_update(request, pk=None):
    question = None
    if pk:
        question = get_object_or_404(Question, pk=pk)
        answers = question.sorted_answers_set

        if question.question_picture:
            question_picture = question.question_picture.name
        else:
            question_picture = ''

        json_answers = json.dumps([{'id': a.id, 'label': a.label, 'text': a.text, 'is_correct': a.is_correct} for a in answers])
    form = QuestionForm(request.POST or None, instance=question)
    if request.POST:
        json_answers = request.POST.get('answers_json', '')
        if form.is_valid():
            question = form.save(commit=False)
            question.answers.all().delete()

            if 'question_picture' in request.POST:
                if request.POST['question_picture'] != '' and request.POST['question_picture'] != question_picture:
                    copy(str(settings.BASE_DIR) + request.POST['question_picture'], settings.MEDIA_ROOT + "/question_pics/")
                    question.question_picture = '/question_pics/' + os.path.basename(request.POST['question_picture'])
                elif request.POST['question_picture'] == '':
                    question.question_picture = None

            question.save()
            answers_obj = json.loads(json_answers)
            for a in answers_obj:
                new_answer = Answer(
                    question=question,
                    label=a['label'],
                    text=a['text'],
                    is_correct=a['is_correct']
                )
                new_answer.save()
            return HttpResponseRedirect('/quiz/update/' + str(question.quiz.id) + '/')
    return render(request, 'main/question_edit.html', {'form': form, 'question': question, 'json_answers': json_answers})

@login_required
def quiz_upload_link(request, quiz_id=None):
    done = False
    this_user = request.user
    quiz_run = None

    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        question = Question.objects.get(quiz=quiz)
        if quiz.author is not None:
            if this_user.profile.group_teacher.id != quiz.author.id:
                #alum is trying to access a quiz created by someone that is not his tutor
                message = _("Estàs intentant accedir a una prova creada per un professor que no és el teu tutor.")
                go_back_to = "group_menu"
                return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to':go_back_to })
        if this_user.profile.is_teacher:
            message = _("No es permet la pujada de materials a professors. Si vols pujar els materials d'un si us plau grup fes servir l'usuari del grup corresponent.")
            go_back_to = "teacher_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    else:
        message = _("Aquesta prova no existeix!")
        go_back_to = "group_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

    #comprovar si ja estava creada
    #exists = QuizRun.objects.filter(taken_by=this_user).filter(quiz=quiz).filter(date_finished__isnull=False).exists()
    exists = QuizRun.objects.filter(taken_by=this_user).filter(quiz=quiz).exists()
    if exists:
        finished = QuizRun.objects.filter(taken_by=this_user).filter(quiz=quiz).filter(date_finished__isnull=False).exists()
        if finished:
            message = _("Ho sentim, però les proves de pujada de fitxer només es poden fer una vegada.")
            go_back_to = "group_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
        else:
            quiz_run = QuizRun.objects.filter(taken_by=this_user).filter(quiz=quiz).first()
    else:
        quiz_run = QuizRun(taken_by=this_user, quiz=quiz, run_number=1)
        quiz_run.save()
        for question in quiz.questions.all():
            qa = QuizRunAnswers(quizrun=quiz_run, question=question)
            qa.save()

    return render(request, 'main/quiz_take_upload.html',{'quiz': quiz, 'quiz_run': quiz_run, 'quiz_run_done': done, 'question':question})


@login_required
def quiz_take_upload(request, quiz_id=None, run_id=None):
    quiz = None
    quiz_run = None
    question = None
    done = False
    this_user = request.user

    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        question = Question.objects.get(quiz=quiz)
        if quiz.author is not None:
            if this_user.profile.group_teacher.id != quiz.author.id:
                #alum is trying to access a quiz created by someone that is not his tutor
                message = _("Estàs intentant accedir a una prova creada per un professor que no és el teu tutor.")
                go_back_to = "group_menu"
                return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to':go_back_to })
    else:
        message = _("Aquesta prova no existeix!")
        go_back_to = "group_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    if run_id:
        quiz_run = get_object_or_404(QuizRun,pk=run_id)
        done = quiz_run.is_done()
        if done:
            message = _("Ho sentim, però les proves de pujada de fitxer només es poden fer una vegada.")
            go_back_to = "group_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

    return render(request, 'main/quiz_take_upload.html',{'quiz': quiz, 'quiz_run': quiz_run, 'quiz_run_done': done, 'question':question})


@login_required
def quiz_take(request, quiz_id=None, question_number=1, run_id=None):
    quiz = None
    quiz_run = None
    question = None
    user_input = None
    previous_question = None
    next_question = None
    questions_total = None
    questions = None
    #current_progress = 0
    step_width = 0
    done = False
    all_questions_answered = False
    this_user = request.user
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        if quiz.author is not None:
          if this_user.profile.group_teacher.id != quiz.author.id:
              #alum is trying to access a quiz created by someone that is not his tutor
              message = _("Estàs intentant accedir a una prova creada per un professor que no és el teu tutor.")
              go_back_to = "group_menu"
              return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to':go_back_to })
        question = Question.objects.get(quiz=quiz,question_order=question_number)
        questions = quiz.sorted_questions_set
        questions_total = questions.count()
        step_width = str(100/questions_total)
        #current_progress = question_number/questions_total
        try:
            previous_question = Question.objects.get(quiz=quiz,question_order=question_number - 1)
        except Question.DoesNotExist:
            pass
        try:
            next_question = Question.objects.get(quiz=quiz,question_order=question_number + 1)
        except Question.DoesNotExist:
            pass
    else:
        raise forms.ValidationError("No existeix aquesta prova")
    if run_id:
        quiz_run = get_object_or_404(QuizRun,pk=run_id)
        done = quiz_run.is_done()
        if done and quiz_run.date_finished is not None:
            message = _("Aquesta prova està marcada com a finalitzada, o sigui que no la pots modificar. Si vols, la pots repetir.")
            go_back_to = "group_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

    user_input = QuizRunAnswers.objects.get(question=question, quizrun=quiz_run)

    completed_questions = QuizRunAnswers.objects.filter(quizrun=quiz_run).filter(answered=True).values('question__id')
    completed_questions_list = [a['question__id'] for a in completed_questions]
    all_questions_answered = quiz_run.all_questions_answered()
    all_quizzes_ordered = get_ordered_quiz_sequence(this_user)

    return render(request, 'main/quiz_take.html',
                  {
                      'quiz': quiz,
                      'quiz_run': quiz_run,
                      'quiz_run_done': done,
                      'user_input': user_input,
                      'question': question,
                      'previous_question':previous_question,
                      'next_question': next_question,
                      #'current_progress': str(current_progress*100),
                      'step_width': step_width,
                      'questions_total': questions_total,
                      'questions': questions,
                      'completed_questions_list': completed_questions_list,
                      'all_questions_answered': all_questions_answered,
                      'all_quizzes_ordered': all_quizzes_ordered
                  })


@login_required
def quiz_start(request, pk=None):
    quiz = None
    questions_total = None
    last_quizrun = None
    this_user = request.user
    if pk:
        quiz = get_object_or_404(Quiz, pk=pk)
        if not quiz.published:
            message = _("Aquesta prova no està publicada, no la pots començar.")
            go_back_to = "group_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
        if quiz.type != 0 and quiz.type != 2:
            #només es poden repetir els tests
            already_done = QuizRun.objects.filter(taken_by=this_user).filter(quiz=quiz).filter(date_finished__isnull=False).exists()
            if already_done:
                message = _("Les proves de materials, pujada de fitxers i enquestes només es fan una vegada. Les pots repassar totes però des del menú de grup ")
                go_back_to = "group_menu"
                return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
        if quiz.type == 2:
            already_done = QuizRun.objects.filter(taken_by=this_user).filter(quiz=quiz).count() >= this_user.profile.n_students_in_group
            if already_done:
                message = _("La enquesta s'ha repetit tants cops com membres té el grup, no es permeten més repeticions.")
                go_back_to = "group_menu"
                return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
        if quiz.requisite:
          done = QuizRun.objects.filter(quiz=quiz.requisite).filter(date_finished__isnull=False).filter(taken_by=this_user).exists()
          if not done:
            message = _("Aquesta prova té un requisit que no s'ha completat: ") + quiz.requisite.name
            go_back_to = "group_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
        if quiz.author is not None:
          if this_user.profile.group_teacher.id != quiz.author.id:
            #group is trying to start a quiz created by someone that is not his tutor
            message = _("Estàs intentant començar una prova creada per un professor que no és el teu tutor.")
            go_back_to = "group_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to':go_back_to })
        if quiz.campaign.id != this_user.profile.campaign.id:
            message = _("La prova que estàs intentant començar forma part d'una campanya anterior, o sigui que no la pots fer. Si us plau, pregunta al teu professor.")
            go_back_to = "group_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
        #check if user has a pending run. If yes, send there
        pending_quizruns = QuizRun.objects.filter(taken_by=this_user).filter(quiz=quiz).filter(date_finished__isnull=True)
        if pending_quizruns.exists():
            pending_quizrun = pending_quizruns.first()
            return HttpResponseRedirect(reverse('quiz_take',kwargs={"quiz_id":quiz.id, "question_number":1, "run_id": pending_quizrun.id}))
        questions_total = quiz.questions.all().count()
        last_quizrun = QuizRun.objects.filter(taken_by=this_user).filter(quiz=quiz).order_by('-run_number').first()
    else:
        raise forms.ValidationError("No existeix aquesta prova")
    return render(request, 'main/quiz_take_splash.html', {'quiz': quiz, 'questions_total': questions_total, 'last_quizrun': last_quizrun} )

@login_required
def quiz_update(request, pk=None):
    quiz = None
    suggested_new_order = 1
    req = None
    this_user = request.user
    if pk:
        quiz = get_object_or_404(Quiz, pk=pk)
        suggested_new_order = quiz.get_next_question_number
    else:
        message = _("Estàs intentant editar una prova que no existeix.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    if this_user.is_superuser:
        form = QuizAdminForm(request.POST or None, instance=quiz)
    elif this_user.profile.is_teacher:
        form = QuizForm(request.POST or None, instance=quiz)
    if request.POST:
        id_requisite = request.POST.get('requisite', '-1')
        if id_requisite is not None and id_requisite != 'None' and id_requisite != '-1' and id_requisite != '':
            req = Quiz.objects.get(pk=int(id_requisite))
        if form.is_valid():
            quiz = form.save(commit=False)
            if this_user.profile.is_teacher:
                quiz.author = this_user
            if this_user.is_superuser:
                quiz.requisite = req
            quiz.save()
            return HttpResponseRedirect('/quiz/list/')
    if this_user.is_superuser:
        return render(request, 'main/quiz_edit.html', {'form': form, 'quiz': quiz, 'new_order': suggested_new_order, 'selected_author': quiz.author, 'selected_requisite': quiz.requisite.id if quiz.requisite is not None else None })
    elif this_user.profile.is_teacher:
        return render(request, 'main/quiz_edit_teacher.html', {'form': form, 'quiz': quiz, 'new_order': suggested_new_order})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})



@login_required
def alum_update(request, pk=None):
    this_user = request.user
    if this_user.is_superuser:
        tutor = None
        if pk:
            alum = get_object_or_404(User, pk=pk)
            tutor = alum.profile.alum_teacher
        else:
            raise forms.ValidationError("No existeix aquest alumne")
        form = AlumUpdateFormAdmin(request.POST or None, instance=alum)
        if request.POST and form.is_valid():
            user = form.save(commit=False)
            user.profile.alum_teacher = form.cleaned_data.get('teacher')
            user.save()
            return HttpResponseRedirect('/alum/list/')
        return render(request, 'main/alum_edit.html', {'form': form, 'alum_id' : pk, 'tutor': tutor} )
    elif this_user.profile and this_user.profile.is_teacher:
        if pk:
            alum = get_object_or_404(User, pk=pk)
        else:
            raise forms.ValidationError("No existeix aquest alumne")
        form = AlumUpdateForm(request.POST or None, instance=alum)
        if request.POST and form.is_valid():
            user = form.save(commit=False)
            user.profile.alum_teacher = this_user
            user.save()
            return HttpResponseRedirect('/alum/list/')
        return render(request, 'main/alum_edit.html', {'form': form, 'alum_id': pk})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})


@login_required
def alum_new(request):
    this_user = request.user
    if this_user.is_superuser:
        if request.method == 'POST':
            form = SimplifiedAlumFormForAdmin(request.POST)
            if form.is_valid():
                user = form.save()
                teacher = form.cleaned_data.get('teacher')
                user.profile.is_alum = True
                user.profile.alum_teacher = teacher
                user.save()
                return HttpResponseRedirect('/alum/list')
        else:
            form = SimplifiedAlumFormForAdmin()
        return render(request, 'main/alum_new.html', {'form': form})
    elif this_user.profile and this_user.profile.is_teacher:
        if request.method == 'POST':
            form = SimplifiedAlumFormForTeacher(request.POST)
            if form.is_valid():
                user = form.save()
                user.profile.is_alum = True
                user.profile.alum_teacher = this_user
                user.save()
                return HttpResponseRedirect('/alum/list')
        else:
            form = SimplifiedAlumFormForTeacher()
        return render(request, 'main/alum_new.html', {'form': form})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})


@login_required
def teacher_new(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SimplifiedTeacherForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            user = form.save()
            center = form.cleaned_data.get('belongs_to')
            user.profile.is_teacher=True
            user.profile.teacher_belongs_to = center
            user.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/teacher/list/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SimplifiedTeacherForm()

    return render(request, 'main/teacher_new.html', {'form': form})


@login_required
def change_password(request, user_id=None):
    this_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password_1']
            this_user.set_password(password)
            this_user.save()
            url = reverse('teacher_list')
            return HttpResponseRedirect(url)
    else:
        form = ChangePasswordForm()
    return render(request, 'main/change_password.html', {'form': form, 'edited_user': this_user})

@login_required
def center_new(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EducationCenterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            center = form.save(commit=False)
            geom_string = form.cleaned_data.get('location')
            if geom_string != '':
                geom_json = json.loads(geom_string)
                feature_geometry = GEOSGeometry(json.dumps(geom_json['features'][0]['geometry']))
                center.location = feature_geometry
            else:
                center.location = None
            center.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/center/list/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EducationCenterForm()

    return render(request, 'main/center_new.html', {'form': form})


def center_to_geojson(center):
    geos = []
    if center.location:
        geos.append({'type': 'Feature', 'properties': {}, 'geometry': json.loads(center.location.json)})
    features = {
        'type': 'FeatureCollection',
        'features': geos
    }
    return json.dumps(features)


@login_required
def center_update(request, pk=None):
    if pk:
        center = get_object_or_404(EducationCenter,pk=pk)
    else:
        raise forms.ValidationError("No existeix aquest centre")
    form = EducationCenterForm(request.POST or None, instance=center)
    geom_text = center_to_geojson(center)
    if request.POST and form.is_valid():
        center = form.save(commit=False)
        geom_string = form.cleaned_data.get('location')
        if geom_string != '':
            geom_json = json.loads(geom_string)
            if len(geom_json['features']) > 0:
                feature_geometry = GEOSGeometry(json.dumps(geom_json['features'][0]['geometry']))
                center.location = feature_geometry
        else:
            center.location = None
        center.save()
        return HttpResponseRedirect('/center/list/')
    return render(request, 'main/center_edit.html', {'form': form, 'center_id' : pk, 'geom': geom_text})


@login_required
def group_update(request, pk=None):
    this_user = request.user
    photo_path = None
    group_password = None
    group_public_name = None
    group_class = None
    username = None
    n_students_in_group = None
    center = ""
    tutor = ""
    centers = EducationCenter.objects.filter(campaign__active=True).order_by('name')
    if pk:
        group = get_object_or_404(User, pk=pk)
        if group.profile and group.profile.group_picture:
            photo_path = group.profile.group_picture.url
        group_password = group.profile.group_password
        group_public_name = group.profile.group_public_name
        group_class = group.profile.group_class
        n_students_in_group = group.profile.n_students_in_group
        username = group.username
        if group.profile.group_teacher:
            tutor = group.profile.group_teacher.id
            center = group.profile.group_teacher.profile.teacher_belongs_to.id
    else:
        raise forms.ValidationError("No existeix aquest grup")
    form = SimplifiedGroupForm(request.POST or None, instance=group)
    if request.method == 'POST':
        tutor = request.POST.get('group_teacher')
        center = request.POST.get('group_center')
        if form.is_valid():
            user = form.save(commit=False)
            user.profile.group_password = form.cleaned_data.get('password1')
            user.profile.group_public_name = form.cleaned_data.get('group_public_name')
            user.profile.group_class = form.cleaned_data.get('group_class')
            user.profile.n_students_in_group = form.cleaned_data.get('n_students_in_group')
            photo_path = form.cleaned_data.get('photo_path')
            if photo_path and photo_path != '' and photo_path != 'None':
                if str(settings.BASE_DIR) + photo_path != settings.MEDIA_ROOT + "/group_pics/" + os.path.basename(photo_path):
                    copy(str(settings.BASE_DIR) + photo_path, settings.MEDIA_ROOT + "/group_pics/")
                    user.profile.group_picture = 'group_pics/' + os.path.basename(photo_path)
            else:
                user.profile.group_picture = None
            if this_user.is_superuser:
                tutor_user = User.objects.get(pk=int(tutor))
            elif this_user.profile and this_user.profile.is_teacher:
                tutor_user = this_user
            user.profile.group_teacher = tutor_user
            user.save()
            return HttpResponseRedirect('/group/list/')
    if this_user.is_superuser:
        return render(request, 'main/group_edit.html', {'form': form, 'group_id' : pk, 'photo_path': photo_path, 'group_password': group_password, 'group_public_name': group_public_name, 'username': username, 'centers':centers, 'tutor': tutor, 'center':center, 'n_students_in_group': n_students_in_group, 'group_class': group_class })
    elif this_user.profile and this_user.profile.is_teacher:
        return render(request, 'main/group_edit_teacher.html', {'form': form, 'group_id': pk, 'photo_path': photo_path, 'group_password': group_password, 'group_public_name': group_public_name, 'username': username, 'n_students_in_group': n_students_in_group, 'group_class': group_class})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

@login_required
def group_new(request):
    this_user = request.user
    photo_path = None
    centers = EducationCenter.objects.filter(campaign__active=True).order_by('name')
    group_teacher = -1
    group_teacher_center_id = -1
    if request.method == 'POST':
        form = SimplifiedGroupForm(request.POST)
        photo_path = request.POST.get('photo_path')
        group_teacher = request.POST.get('group_teacher')
        group_teacher_center_id = request.POST.get('group_center')
        if this_user.is_superuser:
            tutor = User.objects.get(pk=int(group_teacher))
            campaign = Campaign.objects.get(active=True)
        elif this_user.profile and this_user.profile.is_teacher:
            tutor = this_user
            campaign = this_user.profile.campaign
        if form.is_valid():
            user = form.save()
            user.profile.is_group = True
            user.profile.group_password = form.cleaned_data.get('password1')
            user.profile.group_public_name = form.cleaned_data.get('group_public_name')
            user.profile.group_teacher = tutor
            user.profile.campaign = campaign
            user.profile.n_students_in_group = form.cleaned_data.get('n_students_in_group')
            if photo_path != '':
                copy(str(settings.BASE_DIR) + photo_path, settings.MEDIA_ROOT + "/group_pics/")
                user.profile.group_picture = 'group_pics/' + os.path.basename(photo_path)
            else:
                user.profile.group_picture = 'group_pics/noun_group_737669.jpg'

            user.save()

            print(user.profile.group_picture_thumbnail)

            return HttpResponseRedirect('/group/list/')
    else:
        form = SimplifiedGroupForm()
    if this_user.is_superuser:
        return render(request, 'main/group_new.html', {'form': form, 'photo_path': photo_path, 'centers': centers, 'group_teacher': group_teacher, 'group_teacher_center_id': group_teacher_center_id})
    elif this_user.profile and this_user.profile.is_teacher:
        return render(request, 'main/group_new_teacher.html', {'form': form, 'photo_path': photo_path })
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})



@login_required
def teacher_update(request, pk=None):
    if pk:
        teacher = get_object_or_404(User,pk=pk)
        belongs_to = teacher.profile.teacher_belongs_to
    else:
        raise forms.ValidationError("No existeix aquest professor")
    form = TeacherUpdateForm(request.POST or None, instance=teacher)
    if request.POST and form.is_valid():
        user = form.save(commit=False)
        user.profile.teacher_belongs_to = form.cleaned_data.get('belongs_to')
        user.save()
        return HttpResponseRedirect('/teacher/list/')
    return render(request, 'main/teacher_edit.html', {'form': form, 'teacher_id' : pk, 'belongs_to': belongs_to})


@login_required
def group_list(request):
    return render(request, 'main/group_list.html')


@login_required
def group_list_pdf(request):
    this_user = request.user
    search_field_list = ('username', 'group_public_name', 'group_center', 'group_tutor')
    field_translation_list = {'username': 'username', 'group_public_name': 'profile__group_public_name', 'group_center': 'profile__center_string', 'group_tutor': 'profile__group_teacher__username'}
    sort_translation_list = {'username': 'username', 'group_public_name': 'profile__group_public_name', 'group_center': 'profile__center_string', 'group_tutor': 'profile__group_teacher__username'}

    logger = logging.getLogger('weasyprint')
    logger.addHandler(logging.FileHandler('/tmp/weasyprint.log'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment'
    response['Content-Disposition'] = 'filename="test.pdf"'

    if this_user.is_superuser:
        queryset = User.objects.filter(profile__is_group=True).filter(is_active=True)

        data = generic_datatable_list_endpoint(request, search_field_list, queryset, GroupSerializer, field_translation_list, sort_translation_list, paginate=False)
        records = data.data['data']

        grupos_info = []
        teacher_info = []
        for g in records:
            grupos_info.append({
                'nombre_publico_grupo': g['group_public_name'],
                'password_grupo': g['group_password'],
                'nombre_grupo': g['username'],
                'name_profe': g['group_tutor'],
                'center': g['group_center'],
                'hashtag': g['group_hashtag'],
            })

        '''teacher_info.append({
            'name': records[0]['group_tutor'],
            'centro': records[0]['group_center']
        })'''

        html_string = render_to_string("pdf_templates/group_credentials_list_admin.html", {'titulo': _('Llistat de credencials'), 'grupos': grupos_info})
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
        response.write(pdf_file)

    elif this_user.profile and this_user.profile.is_teacher:
        queryset = User.objects.filter(profile__is_group=True).filter(profile__group_teacher=this_user)
        data = generic_datatable_list_endpoint(request, search_field_list, queryset, GroupSerializer, field_translation_list, sort_translation_list, paginate=False)
        records = data.data['data']

        grupos_info = []
        teacher_info = []
        for g in records:
            grupos_info.append({
                'nombre_publico_grupo': g['group_public_name'],
                'password_grupo': g['group_password'],
                'nombre_grupo': g['username'],
                'hashtag': g['group_hashtag']
            })

        teacher_info = {
            'name': records[0]['group_tutor'],
            'centro': records[0]['group_center']
        }

        html_string = render_to_string("pdf_templates/group_credentials_list.html", {'titulo': 'Llistat de credencials', 'teacherInfo': teacher_info, 'grupos': grupos_info})
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
        response.write(pdf_file)

    else:
        queryset = None

    return response
    #return Response(json.loads(json.dumps(records)))


@login_required
def center_list(request):
    return render(request, 'main/center_list.html')


@login_required
def teacher_list(request):
    return render(request, 'main/teacher_list.html')


@login_required
def quiz_list(request):
    this_user = request.user
    if this_user.is_superuser or (this_user.profile and this_user.profile.is_teacher):
        return render(request, 'main/quiz_list.html')
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})


@login_required
def alum_list(request):
    this_user = request.user
    if this_user.is_superuser or (this_user.profile and this_user.profile.is_teacher):
        return render(request, 'main/alum_list.html')
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

@login_required
def open_answer_edit(request, quizcorrection_id=None):
    this_user = request.user
    quizcorrection = QuizCorrection.objects.get(pk=quizcorrection_id)
    quizrun = quizcorrection.corrected_quizrun
    answers = QuizRunAnswers.objects.filter(quizrun=quizrun)
    if this_user.is_superuser:
        #my_quizzes = Quiz.objects.filter(type=0).order_by('name')
        pass
    elif this_user.profile and this_user.profile.is_teacher:
        form = OpenAnswerNewCorrectForm(request.POST or None, instance=quizcorrection)
        if request.POST and form.is_valid():
            correct = form.save(commit=False)
            correct.corrected_quizrun = quizrun
            date_finished = datetime.utcnow().replace(tzinfo=pytz.utc)
            correct.date_finished = date_finished
            correct.corrector = this_user
            correct.save()
            return HttpResponseRedirect('/quiz/open_answer_results/')
        return render(request, 'main/oac_edit.html', {'form': form, 'quizrun': quizrun, 'answers': answers, 'quizcorrection': quizcorrection})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

@login_required
def open_answer_detail(request, quizcorrection_id=None):
    this_user = request.user
    quizcorrection = QuizCorrection.objects.get(pk=quizcorrection_id)
    quizrun = quizcorrection.corrected_quizrun
    answers = QuizRunAnswers.objects.filter(quizrun=quizrun)
    return render(request, 'main/open_answer_detail.html', {'correction': quizcorrection, 'quizrun': quizrun, 'answers': answers})

@login_required
def open_answer_new(request, quizrun_id=None):
    this_user = request.user
    quizrun = QuizRun.objects.get(pk=quizrun_id)
    answers = QuizRunAnswers.objects.filter(quizrun=quizrun)
    if this_user.is_superuser:
        #my_quizzes = Quiz.objects.filter(type=0).order_by('name')
        pass
    elif this_user.profile and this_user.profile.is_teacher:
        if request.method == 'POST':
            form = OpenAnswerNewCorrectForm(request.POST)
            if form.is_valid():
                correct = form.save(commit=False)
                correct.corrected_quizrun = quizrun
                date_finished = datetime.utcnow().replace(tzinfo=pytz.utc)
                correct.date_finished = date_finished
                correct.corrector = this_user
                correct.save()
                return HttpResponseRedirect('/quiz/open_answer_results/')
        else:
            form = OpenAnswerNewCorrectForm()
        return render(request, 'main/oac_new.html', {'form': form, 'quizrun': quizrun, 'answers': answers})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})


@login_required
def open_answer_results(request):
    this_user = request.user
    quiz_array = []
    if this_user.is_superuser:
        #my_quizzes = Quiz.objects.filter(type=0).order_by('name')
        pass
    elif this_user.profile and this_user.profile.is_teacher:
        #my_quizzes = Quiz.objects.filter(author=this_user).filter(type=0).order_by('name')
        teacher_campaign = this_user.profile.campaign
        groups = User.objects.filter(profile__group_teacher=this_user).filter(profile__campaign=teacher_campaign).order_by('profile__group_public_name')
        openanswer_quizzes = Quiz.objects.filter(Q(author=this_user) | Q(author__isnull=True)).filter(type=5).filter(campaign=teacher_campaign).order_by('name')
        for quiz in openanswer_quizzes:
            group_array = []
            for g in groups:
                quizrun = QuizRun.objects.filter(quiz=quiz).filter(taken_by=g).exclude(date_finished=None)
                quizrun_done = quizrun.exists()
                if quizrun_done:
                    the_quizrun = quizrun.first()
                    correction = QuizCorrection.objects.filter(corrected_quizrun=the_quizrun).filter(corrector=this_user).exclude(date_finished=None)
                    corrected = correction.exists()
                    if corrected:
                        the_correction = correction.first()
                        group_array.append({ 'group': g, 'done': True, 'quizrun': the_quizrun, 'corrected': corrected, 'correction': the_correction })
                    else:
                        group_array.append({'group': g, 'done': True, 'quizrun': the_quizrun, 'corrected': corrected, 'correction': None})
                else:
                    group_array.append({ 'group': g, 'done': False, 'quizrun': None, 'corrected': False})
            group_array.sort(key=lambda x: (x['group'].profile.center, x['group'].profile.group_public_name))
            quiz_array.append({ 'quiz': quiz, 'groups': group_array })
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    #print(my_quizzes[1].taken_by[0].taken_by.profile.group_picture_thumbnail.url)
    return render(request, 'main/open_answers_result.html', {'quizzes': quiz_array})

@login_required
def quiz_solutions(request):
    this_user = request.user
    if this_user.is_superuser:
        my_quizzes = Quiz.objects.filter(type=0).order_by('name')
    elif this_user.profile and this_user.profile.is_teacher:
        my_quizzes = Quiz.objects.filter(author=this_user).filter(type=0).order_by('name')
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    #print(my_quizzes[1].taken_by[0].taken_by.profile.group_picture_thumbnail.url)
    return render(request, 'main/test_solutions_teacher.html', {'my_quizzes': my_quizzes})


@api_view(['GET'])
def teachers_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('username','center')
        queryset = User.objects.filter(profile__is_teacher=True).filter(profile__campaign__active=True)
        field_translation_list = {'username': 'username', 'center': 'profile__teacher_belongs_to__name'}
        sort_translation_list = {'username': 'username', 'center': 'profile__teacher_belongs_to__name'}
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, TeacherSerializer, field_translation_list, sort_translation_list)
        return response


def get_random_row(qs):
    qs_count = qs.count()
    random_index = randint(0, qs_count - 1)
    return qs[random_index]


def generate_random_username_struct(locale='en'):
    color = get_random_row(Word.objects.filter(type='color').filter(language=locale).order_by('word'))
    adjective = get_random_row(Word.objects.filter(type='adjective').filter(language=locale).order_by('word'))
    animal = get_random_row(Word.objects.filter(type='animal').filter(language=locale).order_by('word'))
    if locale == 'es':
      group_name = " ".join([animal.word, adjective.word, color.word ])
      group_slug = "_".join([animal.word[0].lower() + adjective.word[0].lower(), color.word.lower()])
    else:
      group_name = " ".join([adjective.word, color.word, animal.word])
      group_slug = "_".join([adjective.word[0].lower() + color.word[0].lower(), animal.word.lower()])
    return {'group_name': group_name, 'group_slug': group_slug}


def get_max_index_plus_one(slug,numerals):
    nums = []
    for elem in numerals:
        num = elem.username.replace(slug,"")
        if num != '':
            nums.append(int(num))
    if len(nums) == 0:
        return 1
    else:
        return max(nums) + 1


@api_view(['POST'])
def api_writeanswer(request):
    if request.method == 'POST':
        id = request.data.get('id', -1)
        answer_id = request.data.get('answer_id', -1)
        open_answer = request.data.get('open_answer', None)

        if id == -1:
            raise ParseError(detail='Quiz run answer id not specified')

        if answer_id == -1:
            answer = None
        else:
            answer = get_object_or_404(Answer, pk=answer_id)

        qra = get_object_or_404(QuizRunAnswers, pk=id)

        qra.chosen_answer = answer
        qra.open_answer = open_answer
        qra.answered = True
        qra.save()

        done = qra.quizrun.is_done()
        endcomments = qra.quizrun.quiz.comment_at_the_end

        serializer = QuizRunAnswerSerializer(qra)

        response = { "done": done, "endcomments": endcomments, "data": serializer.data}

        return Response(response)


def map(request):
    centers = EducationCenter.objects.exclude(location__isnull=True)
    serializer = EducationCenterSerializer(centers, many=True)
    centers = json.dumps(serializer.data)
    count_data = get_center_bs_sites_count()
    count = json.dumps(count_data)
    bs = get_center_bs_sites()
    awards_data = json.dumps(get_center_awards())
    return render(request, 'main/map.html', { 'centers' :  centers, 'count_data': count, 'bs': bs, 'awards_data': awards_data})


def get_center_awards():
    center_awards = {}
    awards_on_centers = Awards.objects.all().values('center').distinct()
    education_center_with_awards = EducationCenter.objects.filter(id__in=awards_on_centers)
    for a in education_center_with_awards:
        center_hash = a.hashtag
        center_awards[center_hash] = True
    return center_awards


def get_center_bs_sites_count():
    count_data = {}
    breeding_sites = BreedingSites.objects.values('center_hashtag').order_by('center_hashtag').annotate(the_count=Count('center_hashtag'))
    for b in breeding_sites:
        count_data[ b['center_hashtag'] ] = b['the_count']
    return count_data


def get_center_bs_sites(campaigns=None):
    sites = {}
    if campaigns:
        breeding_sites = BreedingSites.objects.filter(campaign__in=campaigns).order_by('center_hashtag')
    else:
        breeding_sites = BreedingSites.objects.order_by('center_hashtag')
    for b in breeding_sites:
        try:
            sites[b.center_hashtag]
        except KeyError:
            sites[b.center_hashtag] = []
        serializer = BreedingSiteSerializer(b, many=False)
        sites[b.center_hashtag].append( serializer.data )
    return json.dumps(sites)


def map_campaign_year(request, year=None):
    if year is None:
        centers = EducationCenter.objects.exclude(location__isnull=True)
        serializer = EducationCenterSerializer(centers, many=True)
        centers = json.dumps(serializer.data)
        count_data = get_center_bs_sites_count()
        count = json.dumps(count_data)
        bs = get_center_bs_sites()
        current_year = 0
        awards_data = json.dumps(get_center_awards())
        return render(request, 'main/map.html', {'centers': centers, 'count_data': count, 'bs': bs, 'current_year': current_year, 'awards_data': awards_data})
    else:
        campaigns_year = Campaign.objects.filter(start_date__year=year)
        centers = EducationCenter.objects.filter(campaign__in=campaigns_year).exclude(location__isnull=True)
        serializer = EducationCenterSerializer(centers, many=True)
        centers = json.dumps(serializer.data)
        count_data = get_center_bs_sites_count()
        count = json.dumps(count_data)
        bs = get_center_bs_sites(campaigns_year)
        awards_data = json.dumps(get_center_awards())
        return render(request, 'main/map.html', {'centers': centers, 'count_data': count, 'bs': bs, 'current_year': year, 'awards_data': awards_data})


def map_campaign(request, campaign):
    centers = EducationCenter.objects.filter(campaign__id=campaign).exclude(location__isnull=True)
    serializer = EducationCenterSerializer(centers, many=True)
    centers = json.dumps(serializer.data)
    count_data = get_center_bs_sites_count()
    count = json.dumps(count_data)
    bs = get_center_bs_sites(campaign)
    awards_data = json.dumps(get_center_awards())
    return render(request, 'main/map.html', {'centers': centers, 'count_data': count, 'bs': bs, 'awards_data': awards_data})


def get_number_of_points_center(center):
    hashtag = center.hashtag
    sd_water = BreedingSites.objects.filter(center_hashtag=hashtag).filter(private_webmap_layer='storm_drain_water').count()
    sd_dry = BreedingSites.objects.filter(center_hashtag=hashtag).filter(private_webmap_layer='storm_drain_dry').count()
    sd_other = BreedingSites.objects.filter(center_hashtag=hashtag).filter(private_webmap_layer='breeding_site_other').count()
    total = BreedingSites.objects.filter(center_hashtag=hashtag).count()
    data = {
        "total":  total,
        "sd_water": sd_water,
        "sd_dry": sd_dry,
        "sd_other": sd_other
    }
    return data


def get_participation_years(center):
    center_hash_no_year = center.center_slug(year=False)
    campaigns_by_center = EducationCenter.objects.filter(hashtag__startswith=center_hash_no_year).values('campaign').distinct()
    campaigns = Campaign.objects.filter(id__in=campaigns_by_center)
    years = []
    for c in campaigns:
        years.append( str(c.start_date.year) )
    if len(years) > 0:
        return ','.join(years)
    return ''

@api_view(['GET'])
@permission_classes([AllowAny])
def center_info(request, pk=None):
    if request.method == 'GET':
        center = None
        if pk is None:
            raise ParseError(detail='Center id is mandatory')
        try:
            center = EducationCenter.objects.get(pk=pk)
            participation_years = get_participation_years(center)
            n_points_data = get_number_of_points_center(center)
            awards = Awards.objects.filter(center=center).order_by('age_bracket', 'award')
            context = {
                'center_name': center.name,
                'hashtag': center.hashtag,
                'n_points_total': n_points_data['total'],
                'n_points_water': n_points_data['sd_water'],
                'n_points_dry': n_points_data['sd_dry'],
                'n_points_other': n_points_data['sd_other'],
                'n_groups': center.n_groups_center(),
                'n_students': center.n_students_center(),
                'participation_years': participation_years,
                'awards': awards
            }
            html_data = render_to_string('main/map_bulma_card.html',context=context)
            serializer = EducationCenterSerializer(center)
            return Response({'ec': serializer.data, 'html': html_data})
        except EducationCenter.DoesNotExist:
            raise ParseError(detail='Center Not found')

@api_view(['POST'])
def complete_upload(request):
    if request.method == 'POST':
        quizrun_id = request.data.get('id', -1)
        file_path = request.data.get('path', -1)
        date_finished = datetime.utcnow().replace(tzinfo=pytz.utc)
        if quizrun_id == -1:
            raise ParseError(detail='Quiz id not specified')
        if file_path == -1:
            raise ParseError(detail='File path not specified')
        quizrun = get_object_or_404(QuizRun, pk=quizrun_id)
        quizrun_answer = get_object_or_404(QuizRunAnswers, quizrun=quizrun)
        # file_path should be something like /media/tempfiles/1222b116-6543-11eb-833c-c85b76d93ea4.zip
        if file_path != '':
            copy(str(settings.BASE_DIR) + file_path, settings.MEDIA_ROOT + "/uploaded/")
            quizrun_answer.uploaded_material = 'uploaded/' + os.path.basename(file_path)
            quizrun_answer.answered = True
            quizrun_answer.save()
            quizrun.date_finished = date_finished
            quizrun.save()
            serializer = QuizRunSerializer(quizrun)
            return Response(serializer.data)
        else:
            raise ParseError(detail='Problem with file path')

@api_view(['POST'])
def api_finishquiz(request):
    if request.method == 'POST':
        quizrun_id = request.data.get('id', -1)
        comments = request.data.get('comments', None)
        date_finished = datetime.utcnow().replace(tzinfo=pytz.utc)
        if quizrun_id == -1:
            raise ParseError(detail='Quiz id not specified')
        quizrun = get_object_or_404(QuizRun, pk=quizrun_id)
        quizrun.date_finished = date_finished
        if quizrun.quiz.is_test:
            eval_data = quizrun.evaluate()
            quizrun.questions_number = eval_data['questions_number']
            quizrun.questions_right = eval_data['questions_right']
        if quizrun.quiz.comment_at_the_end:
            quizrun.finishing_comments = comments
        quizrun.save()
        serializer = QuizRunSerializer(quizrun)
        return Response(serializer.data)


@api_view(['POST'])
def api_startrun(request):
    if request.method == 'POST':
        quiz_id = request.data.get('quiz_id', -1)
        taken_by = request.data.get('taken_by', -1)
        run_number = request.data.get('run_number', -1)
        if quiz_id == -1:
            raise ParseError(detail='Quiz id not specified')
        if run_number == -1:
            raise ParseError(detail='Run number not specified')
        else:
            if QuizRun.objects.filter( quiz=quiz_id, taken_by=taken_by, run_number=run_number ).exists():
                return Response('Run number already exists',status=status.HTTP_404_NOT_FOUND)
        quiz = get_object_or_404(Quiz,pk=quiz_id)
        user_taken = get_object_or_404(User,pk=taken_by)
        q = QuizRun(taken_by=user_taken, quiz=quiz, run_number=run_number)
        q.save()
        for question in quiz.questions.all():
            qa = QuizRunAnswers( quizrun=q, question=question )
            qa.save()
        return Response({'run_id': q.id})


@api_view(['GET'])
def get_random_group_name(request, locale='en'):
    if request.method == 'GET':
        if locale not in ['en','es']:
          locale = 'en'
        name_struct = generate_random_username_struct(locale)
        slug = name_struct['group_slug']
        if User.objects.filter(username=slug).exists():
            #check if there are already numerals
            numerals = User.objects.filter(username__startswith=slug)
            n = get_max_index_plus_one(slug,numerals)
            name_struct['group_slug'] = slug + str(n)
        return Response(name_struct)


@api_view(['GET'])
def quiz_datatable_list(request):
    this_user = request.user
    if request.method == 'GET':
        search_field_list = ('name','author.username')
        field_translation_list = {'name': 'name', 'seq': 'seq', 'author.username': 'author__username', 'education_center': 'author__profile__teacher_belongs_to__name'}
        sort_translation_list = {'name': 'name', 'seq': 'seq', 'author.username': 'author__username', 'education_center': 'author__profile__teacher_belongs_to__name' }
        if this_user.is_superuser:
            queryset = Quiz.objects.select_related('author').filter(campaign__active=True).all()
        elif this_user.profile.is_teacher:
            queryset = Quiz.objects.select_related('author').filter(campaign=this_user.profile.campaign).filter(author=this_user)
        else:
            pass  # this should not happen
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, QuizSerializer, field_translation_list, sort_translation_list)
        return response


@api_view(['GET'])
def centers_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('name','hashtag')
        queryset = EducationCenter.objects.filter(campaign__active=True).all()
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, EducationCenterSerializer)
        return response


@api_view(['GET'])
def alum_datatable_list(request):
    this_user = request.user
    if request.method == 'GET':
        search_field_list = ('username','teacher','groups')
        if this_user.is_superuser:
            queryset = User.objects.filter(profile__is_alum=True)
        elif this_user.profile.is_teacher:
            queryset = User.objects.filter(profile__is_alum=True).filter(profile__alum_teacher=this_user)
        else:
            pass #this should not happen
        field_translation_list = {'username': 'username', 'teacher': 'profile__alum_teacher__username', 'groups': 'profile__groups_string'}
        sort_translation_list = {'username': 'username', 'teacher': 'profile__alum_teacher__username', 'groups': 'profile__groups_string'}
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, AlumSerializer, field_translation_list, sort_translation_list)
        return response


@api_view(['GET'])
def group_datatable_list(request):
    this_user = request.user
    if request.method == 'GET':
        search_field_list = ('username', 'group_public_name', 'group_center', 'group_tutor', 'group_n_students', 'group_class')
        if this_user.is_superuser:
            queryset = User.objects.filter(profile__is_group=True).filter(profile__campaign__active=True)
        elif this_user.profile and this_user.profile.is_teacher:
            #groups that contain any of the tutorees
            # tutorized_alums = User.objects.filter(profile__is_alum=True).filter(profile__alum_teacher=this_user)
            # group_ids = []
            # for t_alum in tutorized_alums:
            #     groups = t_alum.profile.alum_in_group.all().values('id')
            #     group_ids += [a['id'] for a in groups]
            # queryset = User.objects.filter(profile__is_group=True).filter(id__in=group_ids)
            queryset = User.objects.filter(profile__is_group=True).filter(profile__group_teacher=this_user).filter(profile__campaign=this_user.profile.campaign)
        else:
            pass #not allowed
        field_translation_list = {'username': 'username', 'group_public_name': 'profile__group_public_name', 'group_class': 'profile__group_class', 'group_center': 'profile__center_string', 'group_tutor':  'profile__group_teacher__username', 'group_n_students': 'profile__n_students_in_group'}
        sort_translation_list = {'username': 'username', 'group_public_name': 'profile__group_public_name', 'group_class': 'profile__group_class', 'group_center': 'profile__center_string', 'group_tutor':  'profile__group_teacher__username', 'group_n_students': 'profile__n_students_in_group'}
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, GroupSerializer, field_translation_list, sort_translation_list)
        return response


@api_view(['GET'])
def group_search(request):
    if request.method == 'GET':
        q = request.query_params.get('q','')
        if q != '':
            queryset = User.objects.filter(profile__is_group=True).filter(profile__group_public_name__icontains=q).order_by('profile__group_public_name')
        else:
            queryset = User.objects.filter(profile__is_group=True).order_by('profile__group_public_name')
        serializer = GroupSearchSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def quiz_search(request):
    if request.method == 'GET':
        q = request.query_params.get('q', '')
        tutor_id = request.query_params.get('tutor_id', '-1')
        t_id = int(tutor_id)
        if q != '':
            queryset = Quiz.objects.filter(author__id=t_id).filter(name__icontains=q).order_by('name')
        else:
            queryset = Quiz.objects.filter(author__id=t_id).order_by('name')
        serializer = QuizSearchSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def alum_search(request):
    if request.method == 'GET':
        this_user = request.user
        q = request.query_params.get('q', '')
        if this_user.is_superuser:
            tutor_id = request.query_params.get('tutor_id', '-1')
            t_id = int(tutor_id)
        elif this_user.profile and this_user.profile.is_teacher:
            t_id = this_user.id
        else:
            pass #Security exception
        if q != '':
            queryset = User.objects.filter(profile__is_alum=True).filter(username__icontains=q).filter(profile__alum_teacher__id=t_id).order_by('username')
        else:
            queryset = User.objects.filter(profile__is_alum=True).filter(profile__alum_teacher__id=t_id).order_by('username')
        serializer = AlumSearchSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def requirements_combo(request):
    if request.method == 'GET':
        q = request.query_params.get('author_id', -1)
        if q == '-1':
          # is admin
          queryset = Quiz.objects.filter(author__isnull=True).filter(campaign__active=True).order_by('name')
        else:
          queryset = Quiz.objects.filter(author__id=q).order_by('name')
        serializer = QuizComboSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def group_combo(request):
    if request.method == 'GET':
        q = request.query_params.get('center_id', -1)
        if q == -1:
            queryset = User.objects.filter(profile__is_group=True).order_by('profile__group_public_name')
        else:
            center = EducationCenter.objects.get(pk=q)
            queryset = User.objects.filter(profile__center_string=center.name).filter(profile__campaign=center.campaign).order_by('profile__group_public_name')
        serializer = GroupComboSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def tutor_combo(request):
    if request.method == 'GET':
        q = request.query_params.get('center_id','')
        if q != '':
            queryset = User.objects.filter(profile__is_teacher=True).filter(profile__teacher_belongs_to__id=q).order_by('username')
        else:
            queryset = User.objects.filter(profile__is_teacher=True).order_by('username')
        serializer = GroupComboSerializer(queryset, many=True)
        return Response(serializer.data)


@login_required
def uploadpic(request):
    this_user = request.user
    if this_user.is_superuser or (this_user.profile is not None and this_user.profile.is_teacher):
        if request.method == 'POST':
            file = request.FILES
            f = request.FILES['camp_foto']
            with open(settings.MEDIA_ROOT + "/tempfiles/" + f.name, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            data = {'is_valid': True, 'id':1, 'url':'/media/tempfiles/'+f.name, 'path':settings.MEDIA_ROOT + "/tempfiles/" + f.name}
            return JsonResponse(data)

@login_required
def uploadfile(request):
    if request.method == 'POST':
        f = request.FILES['camp_file']
        new_name = str(uuid.uuid1()) + ".zip"
        with open(settings.MEDIA_ROOT + "/tempfiles/" + new_name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        data = {'is_valid': True, 'id': 1, 'url': '/media/tempfiles/' + new_name,
                'path': settings.MEDIA_ROOT + "/tempfiles/" + f.name}
        return JsonResponse(data)

@login_required
def upload_question_pic(request):
    this_user = request.user
    if this_user.is_superuser or (this_user.profile is not None and this_user.profile.is_teacher):
        if request.method == 'POST':
            file = request.FILES
            f = request.FILES['question_foto']
            with open(settings.MEDIA_ROOT + "/tempfiles/" + f.name, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            data = {'is_valid': True, 'id': 1, 'url': '/media/tempfiles/' + f.name,
                    'path': settings.MEDIA_ROOT + "/tempfiles/" + f.name}
            return JsonResponse(data)




class CentersViewSet(viewsets.ModelViewSet):
    queryset = EducationCenter.objects.all()
    serializer_class = EducationCenterSerializer


class QuestionsViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuizzesViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class AdminOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        this_user = request.user
        if this_user.is_superuser:
            return True
        return False


class AdminOrTeacherOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        this_user = request.user
        if this_user.is_superuser:
            return True
        if this_user.profile is not None:
            if this_user.profile.is_teacher:
                return True
        return False


@permission_classes([AdminOrTeacherOnlyPermission])
class UserPartialUpdateView(GenericAPIView, UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


@permission_classes([AdminOnlyPermission])
class EducationCenterPartialUpdateView(GenericAPIView, UpdateModelMixin):
    '''
    You just need to provide the field which is to be modified.
    '''
    queryset = EducationCenter.objects.all()
    serializer_class = EducationCenterSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

@login_required
def group_credentials_list(request):
    this_user = request.user.id

    centroID = Profile.objects.filter(user=request.user).values('teacher_belongs_to_id')
    centro = get_object_or_404(EducationCenter, pk=centroID[0]['teacher_belongs_to_id'])


    teacher_info = []
    teacher_info = {
        'name': request.user.username,
        'centro': centro.name
    }

    #grupos = Profile.objects.filter(is_group=True).filter(group_teacher=this_user)

    #queryset = User.objects.filter(profile__is_group=True).filter(profile__group_teacher=this_user).select_related()
    #print(queryset)

    cursor = connection.cursor()
    cursor.execute('select main_profile.user_id as id, main_profile.group_public_name, main_profile.group_password, '
                   'auth_user.username from public.main_profile, public.auth_user '
                   'where main_profile.user_id = auth_user.id and main_profile.group_teacher_id = %s ', [this_user])
    queryset = cursor.fetchall()
    #b'select main_profile.user_id, main_profile.group_public_name, main_profile.group_password, auth_user.username from public.main_profile, public.auth_user where main_profile.user_id = auth_user.id and main_profile.group_teacher_id = 2 '

    test = Profile.objects.raw("select m.user_id, m.group_public_name, m.group_password, a.username from public.main_profile m, auth_user a where m.user_id = a.id and m.group_teacher_id = 2")

    grupos_info = []

    for g in queryset:
        grupos_info.append({
            'nombre_publico_grupo': g[1],
            'password_grupo': g[2],
            'nombre_grupo': g[3]
        })

    logger = logging.getLogger('weasyprint')
    logger.addHandler(logging.FileHandler('/tmp/weasyprint.log'))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment'
    response['Content-Disposition'] = 'filename="test.pdf"'
    html_string = render_to_string("pdf_templates/group_credentials_list.html", {'titulo': 'Llistat de credencials', 'teacherInfo': teacher_info, 'grupos': grupos_info})
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    #pdf_file = HTML(string=html_string, base_url=settings.STATIC_PDF_ROOT).write_pdf()
    response.write(pdf_file)

    return response


@login_required
def quiz_graphic_results(request, idQuizz):
    this_user = request.user
    repeated_tests = []
    tests = []
    grupos_tests = []

    quiz = Quiz.objects.get(pk=idQuizz)
    if request.user.is_superuser:
        grupos_profe = User.objects.filter(profile__is_group=True)
    else:
        grupos_profe = User.objects.filter(profile__group_teacher=request.user.id).filter(profile__is_group=True)

    for x in grupos_profe:

        p = QuizRun.objects.filter(quiz_id=idQuizz).filter(taken_by_id=x.id).exclude(date_finished=None)
        if not p:
            print('Vacio')
        else:
            if p.count() > 1:
                for d in p:
                    repeated_tests.append({
                        'id': d.id,
                        'quiz': d.quiz.name,
                        'quiz_id': d.quiz_id,
                        'taken_by': d.taken_by.username,
                        'questions_number': d.questions_number,
                        'questions_right': d.questions_right

                    })

                sorted_list = sorted(repeated_tests, key=lambda k: k['questions_right'], reverse=True)

                grupos_tests.append(sorted_list[0])
            else:
                for t in p:
                    tests.append({
                        'id': t.id,
                        'quiz': t.quiz.name,
                        'quiz_id': t.quiz_id,
                        'taken_by': t.taken_by.username,
                        'questions_number': t.questions_number,
                        'questions_right': t.questions_right

                    })
    grupos_tests.append(tests)


    return render(request, 'main/quiz_results_graphics.html', {'grupos_tests': grupos_tests, 'quiz': quiz})


@login_required
def quiz_results(request):
     return render(request, 'main/quiz_results.html')

@api_view(['GET'])
def quiz_datatable_results(request):
    this_user = request.user

    if request.method == 'GET':

        search_field_list = ('name', 'author.username')
        field_translation_list = {'name': 'name', 'author.username': 'author__username'}
        sort_translation_list = {'name': 'name', 'author.username': 'author__username'}

        if this_user.is_superuser:
            #queryset = Quiz.objects.select_related('author').all()
            queryset = Quiz.objects.filter(Q(type=0) | Q(type=2) | Q(type=4)).filter(campaign__active=True)
        elif this_user.profile.is_teacher:
            queryset = Quiz.objects.select_related('author').filter(Q(author=this_user) | Q(author__isnull=True)).filter(Q(type=0) | Q(type=2)).filter(campaign=this_user.profile.campaign)
        else:
            pass  # this should not happen
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, QuizSerializer, field_translation_list, sort_translation_list)
    return response



@login_required
def test_result(request, quiz_id=None):
    this_user = request.user
    quiz = None
    if this_user.is_superuser:
        if quiz_id:
            quiz = get_object_or_404(Quiz, pk=quiz_id)
        else:
            message = _("No existeix aquesta prova.")
            go_back_to = "quiz_results"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
        if not QuizRun.objects.filter(quiz=quiz).exists():
            message = _("El test seleccionat no l'ha realitzat cap grup i encara no té resultats.")
            go_back_to = "quiz_results"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
        return render(request, 'main/test_result.html', {'quiz': quiz})
    else:
        best_runs = []
        author = User.objects.get(id=this_user.id)
        grupos_profe = User.objects.filter(profile__group_teacher=author)
        for r in grupos_profe:
            best_run = QuizRun.objects.filter(taken_by__id=r.id).filter(quiz=quiz_id).filter(
                date_finished__isnull=False).order_by('-questions_right', '-date_finished').first()
            if best_run:
                best_runs.append(best_run)
        best_runs.sort(key=lambda x: (x.taken_by.profile.group_public_name if x.taken_by.profile.group_public_name is not None else x.taken_by.username))
        n_of_best_runs = best_runs.__len__()

        if quiz_id:
            quiz = get_object_or_404(Quiz, pk=quiz_id)
        else:
            message = _("No existeix aquesta prova.")
            go_back_to = "quiz_results"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
        if not QuizRun.objects.filter(quiz=quiz).exists():
            message = _("El test seleccionat no l'ha realitzat cap grup i encara no té resultats.")
            go_back_to = "quiz_results"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

        return render(request, 'main/test_result.html', {'quiz': quiz, 'quizRuns': best_runs, 'n_of_best_runs': n_of_best_runs})


@login_required
def upload_file_solutions(request):
    this_user = request.user
    p = []
    uploadedFileFlag = False

    if this_user.is_superuser:
        my_quizzes = Quiz.objects.filter(type=3).filter(campaign__active=True).order_by('name')
        # Recorrer cada upload File test
        for idQuizz in my_quizzes:
            arrayGrupos = []
            grupos_profe = User.objects.filter(profile__group_teacher__isnull=False).filter(profile__campaign__active=True).order_by('profile__group_public_name')

            #Afegir flag per saber quins grups han fet la entrega
            for grupo in grupos_profe:
                quizrun = QuizRun.objects.filter(quiz=idQuizz).filter(taken_by=grupo).exclude(date_finished=None)
                upload_done = quizrun.exists()

                if upload_done:
                    url_pic = ''
                    try:
                        url_pic = grupo.profile.group_picture_thumbnail_small.url
                    except:
                        pass
                    arrayGrupos.append({
                        'imagenGrupo': url_pic,
                        'nombreGrupo': grupo.profile.group_public_name,
                        'centro': grupo.profile.center,
                        'uploadedFileFlag': True,
                        'linkFile': quizrun[0].uploaded_file,
                        'uploadDate': quizrun[0].date_finished
                    })
                else:
                    url_pic = ''
                    try:
                        url_pic = grupo.profile.group_picture_thumbnail_small.url
                    except:
                        pass
                    arrayGrupos.append({
                        'imagenGrupo': url_pic,
                        'nombreGrupo': grupo.profile.group_public_name,
                        'centro': grupo.profile.center,
                        'uploadedFileFlag': False,
                        'linkFile': None,
                        'uploadDate': None
                    })
            arrayGrupos.sort(key=lambda x: (x['centro'], x['nombreGrupo']))
            #Crear array amb informacio de cada prova
            autor = _('Anònim')
            realitzat_per = str(idQuizz.taken_by_n_people)
            if idQuizz.author:
                autor = idQuizz.author.username
                realitzat_per = str(idQuizz.taken_by_n_people) + '/' + str(idQuizz.author.profile.tutored_groups)
            p.append({
                'nomActivitat': idQuizz.name,
                'autor': autor,
                'realitzatPer': realitzat_per,
                'grupos': arrayGrupos
            })
    elif this_user.profile and this_user.profile.is_teacher:
        teacher_campaign = this_user.profile.campaign
        my_quizzes = Quiz.objects.filter(Q(author=this_user) | Q(author__isnull=True)).filter(type=3).filter(campaign=teacher_campaign).order_by('name')

        for idQuizz in my_quizzes:
            arrayGrupos = []
            grupos_profe = User.objects.filter(profile__group_teacher=this_user).filter(profile__campaign=teacher_campaign).order_by('profile__group_public_name')

            #Afegir flag per saber quins grups han fet la entrega
            for grupo in grupos_profe:
                quizrun = QuizRun.objects.filter(quiz=idQuizz).filter(taken_by=grupo).exclude(date_finished=None)
                upload_done = quizrun.exists()

                if upload_done:
                    url_pic = ''
                    try:
                        url_pic = grupo.profile.group_picture_thumbnail_small.url
                    except:
                        pass
                    arrayGrupos.append({
                        'imagenGrupo': url_pic,
                        'nombreGrupo': grupo.profile.group_public_name,
                        'centro': grupo.profile.center,
                        'uploadedFileFlag': True,
                        'linkFile': quizrun[0].uploaded_file,
                        'uploadDate': quizrun[0].date_finished
                    })
                else:
                    url_pic = ''
                    try:
                        url_pic = grupo.profile.group_picture_thumbnail_small.url
                    except:
                        pass
                    arrayGrupos.append({
                        'imagenGrupo': url_pic,
                        'nombreGrupo': grupo.profile.group_public_name,
                        'centro': grupo.profile.center,
                        'uploadedFileFlag': False,
                        'linkFile': None,
                        'uploadDate': None
                    })
            arrayGrupos.sort(key=lambda x: (x['centro'], x['nombreGrupo']))
            #Crear array amb informacio de cada prova
            autor = _('Anònim')
            if idQuizz.author:
                autor = idQuizz.author.username
            p.append({
                'nomActivitat': idQuizz.name,
                'autor': autor,
                'realitzatPer': str(idQuizz.taken_by_n_people) + '/' + str(this_user.profile.tutored_groups),
                'grupos': arrayGrupos
            })
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    return render(request, 'main/upload_file_solutions.html', {'my_quizzes': my_quizzes, 'grupos_profe': p})



@login_required
def quizrun_group_list(request, quiz_id=None, group_id=None):
    this_user = request.user
    quizruns = None
    if quiz_id and group_id:
        #quiz = get_object_or_404(Quiz, pk=quiz_id)
        quizruns = QuizRun.objects.filter(quiz_id=quiz_id).filter(taken_by_id=group_id)
    else:
        message = _("No existeix aquesta prova.")
        go_back_to = "quiz_results"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

    if not quizruns:
        message = _("El test seleccionat no l'ha realitzat cap grup i encara no té resultats.")
        go_back_to = "quiz_results"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

    return render(request, 'main/quizrun_group_list.html', {'quizruns': quizruns})


@api_view(['POST'])
@login_required
def delete_quizrun(request, quizrun_id=None):
    print(quizrun_id)
    if quizrun_id:
        QuizRun.objects.filter(id=quizrun_id).delete()

    context = {}
    return Response(context)

@login_required
def test_results_detail_view(request, quiz_id=None, group_id=None):

    quizruns = QuizRun.objects.filter(quiz_id=quiz_id).filter(taken_by=group_id).exclude(date_finished__isnull=True).order_by('-run_number')

    quizrun_ids = quizruns.values('id')
    quizrun_answers = QuizRunAnswers.objects.filter(quizrun__id__in=quizrun_ids)
    answers_by_quizrun = [str(a.quizrun.id) + '-' + str(a.chosen_answer.id) for a in quizrun_answers]

    quiz = get_object_or_404(Quiz, pk=quiz_id)
    group = get_object_or_404(User, pk=group_id)

    return render(request, 'main/test_results_detail_view.html', {'quizruns': quizruns, 'answers_by_quizrun': answers_by_quizrun, 'quiz_info': quiz, 'group_info': group})

@login_required
def reports(request):
    this_user = request.user
    my_groups = None
    if this_user.profile.is_teacher:
        my_groups = User.objects.filter(profile__is_group=True).filter(profile__group_teacher=this_user).filter(profile__campaign=this_user.profile.campaign).order_by('profile__group_public_name')
        centers = EducationCenter.objects.filter(active=True).filter(campaign=this_user.profile.campaign).order_by('name')
        polls = Quiz.objects.filter(type=2).filter(campaign=this_user.profile.campaign).order_by('name')
        teacher_polls = None
    elif this_user.is_superuser:
        my_groups = User.objects.filter(profile__is_group=True).filter(profile__group_teacher=this_user).filter(profile__campaign__active=True).order_by('profile__group_public_name')
        centers = EducationCenter.objects.filter(active=True).filter(campaign__active=True).order_by('name')
        polls = Quiz.objects.filter(type=2).filter(campaign__active=True).order_by('name')
        teacher_polls = Quiz.objects.filter(type=4).filter(campaign__active=True).order_by('name')
    return render(request, 'main/reports.html', { "centers":centers, "polls":polls, "teacher_polls": teacher_polls, "my_groups":my_groups })

@login_required
def center_progress(request, center_id=None):
    center = get_object_or_404(EducationCenter, pk=center_id)
    center_groups = center.center_groups()
    data = {}
    for group in center_groups:
        quizzes_doable_by_group = group.profile.available_tests
        for quiz in quizzes_doable_by_group:
            state = 'pending'
            uploaded_file = None
            correction_id = None
            quiz_in_progress = QuizRun.objects.filter(taken_by=group).filter(date_finished__isnull=True).filter(quiz=quiz).exists()
            quiz_done = QuizRun.objects.filter(taken_by=group).filter(date_finished__isnull=False).filter(quiz=quiz).exists()
            corrected = False
            if quiz.type == 3:
                uploaded_file_quizrun = QuizRun.objects.filter(taken_by=group).filter(date_finished__isnull=False).filter(quiz__type=3).first()
                if uploaded_file_quizrun is not None:
                    uploaded_file = uploaded_file_quizrun.uploaded_file.url
            elif quiz.type == 5:
                if quiz_done:
                    the_quiz_done = QuizRun.objects.filter(taken_by=group).filter(date_finished__isnull=False).filter(quiz=quiz).first()
                    corrected = QuizCorrection.objects.filter( corrected_quizrun = the_quiz_done ).filter(date_finished__isnull=False).exists()
                    if corrected:
                        the_correction = QuizCorrection.objects.filter( corrected_quizrun = the_quiz_done ).filter(date_finished__isnull=False).first()
                        correction_id = the_correction.id


            # quiz_done is checked first because it might happen that the group has started a new quiz run and left it blank
            # this way, if at least one is done it's considered completed, and only if not a single run has been completed is
            # considered 'in progress'
            if quiz_done:
                if quiz.type == 5:
                    if corrected:
                        state = 'corrected'
                    else:
                        state = 'pending_correction'
                else:
                    state = 'done'
            elif quiz_in_progress:
                state = 'progress'

            data[ str(group.id) + '_' + str(quiz.id) ] = { 'state': state, 'type': quiz.type, 'upload_url': uploaded_file, 'correction_id': correction_id }
    return render(request, 'main/reports/progress_center.html', {'center': center, 'data': json.dumps(data)})


@login_required
def reports_teacher_poll_center(request, poll_id=None, center_id=None):
    if center_id is None:
        poll = get_object_or_404(Quiz, pk=poll_id)
        center = None
        data = {}
        quizrun_completed_by_teachers = QuizRun.objects.filter(quiz=poll).exclude(date_finished__isnull=True).count()
        if quizrun_completed_by_teachers > 0:
            for question in poll.sorted_questions_set:
                for answer in question.sorted_answers_set:
                    data[str(question.id) + '_' + str(answer.id)] = {
                        'n': answer.how_many_times_answered,
                        'total': answer.question.total_number_of_answers_of_question,
                        'perc': answer.answered_by_perc}
    else:
        poll = get_object_or_404(Quiz, pk=poll_id)
        center = get_object_or_404(EducationCenter, pk=center_id)
        data = {}
        teachers_in_center = User.objects.filter(profile__is_teacher=True).filter(profile__teacher_belongs_to=center).values('id').distinct()
        quizruns_in_center_completed_by_teacher = QuizRun.objects.filter(quiz=poll).filter(taken_by_id__in=teachers_in_center).exclude(date_finished__isnull=True).count()
        if quizruns_in_center_completed_by_teacher > 0:
            for question in poll.sorted_questions_set:
                for answer in question.sorted_answers_set:
                    data[str(question.id) + '_' + str(answer.id)] = {
                        'n': answer.how_many_times_answered_by_center_teachers(center.id),
                        'total': answer.question.total_number_of_answers_of_question_per_center_teachers(center.id),
                        'perc': answer.answered_by_perc_center_teachers(center.id)}

    return render(request, 'main/reports/poll_center_or_group.html', {'quiz': poll, 'data': json.dumps(data), 'len_data': len(data), 'center': center})


@login_required
def reports_poll_center_or_group(request, poll_id=None, center_id=None, group_id=None):
    if group_id is None:
        poll = get_object_or_404(Quiz, pk=poll_id)
        center = get_object_or_404(EducationCenter, pk=center_id)
        group = None
        data = {}
        groups_in_center = User.objects.filter(profile__is_group=True).filter(profile__center_string=center.name).values('id').distinct()
        quizruns_in_center_completed = QuizRun.objects.filter(quiz=poll).filter(taken_by_id__in=groups_in_center).exclude(date_finished__isnull=True).count()
        if quizruns_in_center_completed > 0:
            for question in poll.sorted_questions_set:
                for answer in question.sorted_answers_set:
                    data[str(question.id) + '_' + str(answer.id)] = {
                        'n': answer.how_many_times_answered_by_center(center.id),
                        'total': answer.question.total_number_of_answers_of_question_per_center(center.id),
                        'perc': answer.answered_by_perc_center(center.id)}
    else:
        poll = get_object_or_404(Quiz, pk=poll_id)
        center = get_object_or_404(EducationCenter, pk=center_id)
        group = get_object_or_404(User, pk=group_id)
        data = {}
        if poll.is_completed_by(group_id):
            for question in poll.sorted_questions_set:
                for answer in question.sorted_answers_set:
                    data[str(question.id) + '_' + str(answer.id)] = {
                        'n': answer.how_many_times_answered_by_group(group.id),
                        'total': answer.question.total_number_of_answers_of_question_per_group(group.id),
                        'perc': answer.answered_by_perc_group(group.id)}


    return render(request, 'main/reports/poll_center_or_group.html', {'quiz': poll, 'data': json.dumps(data),'len_data': len(data), 'group': group, 'center': center})


@login_required
def campaign_new(request):
    this_user = request.user
    if this_user.is_superuser:
        if request.method == 'POST':
            form = CampaignForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/campaign/list')
        else:
            form = CampaignForm()
        return render(request, 'main/campaign_new.html', {'form': form})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})


@login_required
def campaign_list(request):
    this_user = request.user
    if this_user.is_superuser:
        return render(request, 'main/campaign_list.html', {})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

@api_view(['GET'])
def campaign_datatable_list(request):
    this_user = request.user

    if request.method == 'GET':

        search_field_list = ('name', 'start_date','end_date', 'active')
        field_translation_list = {'name': 'name', 'start_date': 'start_date', 'end_date': 'end_date', 'active': 'active'}
        sort_translation_list = {'name': 'name', 'start_date': 'start_date', 'end_date': 'end_date', 'active': 'active'}

        if this_user.is_superuser:
            queryset = Campaign.objects.all().order_by('name')
        else:
            pass  # this should not happen
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, CampaignSerializer, field_translation_list, sort_translation_list)
    return response


@api_view(['POST'])
def toggle_campaign_active(request):
    if request.method == 'POST':
        id = request.POST.get('id', -1)
        if id == -1:
            raise ParseError(detail='Campaign id not specified')
        campaign = get_object_or_404(Campaign,pk=id)
        if campaign.active:
            raise ParseError(detail='Operation not allowed')
        Campaign.objects.all().update(active=False)
        campaign.active = True
        campaign.save()
        return Response({"ok":True})

@login_required
def campaign_update(request, pk=None):
    this_user = request.user
    if pk:
        campaign = get_object_or_404(Campaign, pk=pk)
    else:
        raise forms.ValidationError("No existeix aquesta campanya")
    form = CampaignForm(request.POST or None, instance=campaign)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/campaign/list/')
    if this_user.is_superuser:
        return render(request, 'main/campaign_edit.html', {'form': form, 'campaign_id' : pk })
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
