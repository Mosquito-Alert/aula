from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from main.forms import QuizForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from main.models import EducationCenter, Word, Quiz, Answer, Question, QuizRun, QuizRunAnswers
from main.forms import TeacherForm, SimplifiedTeacherForm, EducationCenterForm, TeacherUpdateForm, ChangePasswordForm, \
    SimplifiedAlumForm, SimplifiedGroupForm, AlumUpdateForm, QuestionForm, QuestionLinkForm, SimplifiedAlumFormForTeacher, \
    SimplifiedAlumFormForAdmin, AlumUpdateFormAdmin, QuizAdminForm, QuestionPollForm, QuizNewForm
from django.contrib.gis.geos import GEOSGeometry
from rest_framework.decorators import api_view, permission_classes
from querystring_parser import parser
import json
import functools
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import operator
from main.serializers import EducationCenterSerializer, TeacherSerializer, UserSerializer, AlumSerializer, \
    GroupSerializer, GroupSearchSerializer, TeacherComboSerializer, AlumSearchSerializer, QuizSerializer, \
    QuestionSerializer, QuizSearchSerializer, QuizRunAnswerSerializer, QuizRunSerializer, QuizComboSerializer
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


def generic_datatable_list_endpoint(request,search_field_list,queryset, classSerializer, field_translation_dict=None, order_translation_dict=None):
    draw = request.query_params.get('draw', -1)
    start = request.query_params.get('start', 0)
    #length = request.query_params.get('length', 25)
    length = 25

    get_dict = parser.parse(request.GET.urlencode())

    order_clause = get_order_clause(get_dict, order_translation_dict)

    filter_clause = get_filter_clause(get_dict, search_field_list, field_translation_dict)

    if len(filter_clause) == 0:
        queryset = queryset.order_by(*order_clause)
    else:
        queryset = queryset.order_by(*order_clause).filter(functools.reduce(operator.or_, filter_clause))

    paginator = Paginator(queryset, length)

    recordsTotal = queryset.count()
    recordsFiltered = recordsTotal
    page = int(start) / int(length) + 1

    serializer = classSerializer(paginator.page(page), many=True)
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


def index(request):
    return render(request, 'main/index.html', {})


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
        response = redirect('/alum_menu')
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
        go_back_to = "alum_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})


@login_required
def admin_menu(request):
    if request.user.is_superuser:
        return render(request, 'main/admin_menu.html', {})
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        if request.user.profile.is_alum:
            go_back_to = "alum_menu"
        elif request.user.profile.is_teacher:
            go_back_to = "teacher_menu"
        else:
            go_back_to = "index"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})


@login_required
def alum_menu(request):
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


@login_required
def group_menu(request):
    this_user = request.user
    teach = this_user.profile.group_teacher
    quizzes_in_progress_ids = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=True).values('quiz__id').distinct()
    quizzes_done_ids = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).values('quiz__id').distinct()
    available_quizzes = Quiz.objects.filter(author=teach).filter(published=True).exclude(id__in=quizzes_in_progress_ids).exclude(id__in=quizzes_done_ids).order_by('id')
    in_progress_quizruns = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=True).order_by('-date')
    done_quizruns = QuizRun.objects.filter(taken_by=this_user).filter(date_finished__isnull=False).order_by('-date')
    done_quizzes_ids = [ a.quiz.id for a in done_quizruns ]
    #in_progress_quizzes = Quiz.objects.filter(id__in=quizzes_in_progress_ids).order_by('id')
    #done_quizzes = Quiz.objects.filter(id__in=quizzes_done_ids).order_by('id')
    return render(request, 'main/alum_hub.html', {'available_quizzes':available_quizzes, 'in_progress_quizruns':in_progress_quizruns, 'done_quizruns': done_quizruns, 'done_quizzes_ids': done_quizzes_ids})


@login_required
def quiz_new(request):
    this_user = request.user
    if this_user.is_superuser:
        if request.method == 'POST':
            form = QuizAdminForm(request.POST)
            if form.is_valid():
                pre_quiz = form.save(commit=False)
                id_requisite = request.POST.get('requisite', '')
                if id_requisite != -1:
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
        raise forms.ValidationError("No existeix aquesta prova")
    return render(request, 'main/quiz_take_endsummary.html', {'quizrun': quizrun, 'n_runs': n_runs, 'past_runs': past_runs})


@login_required
def quiz_assign_admin(request):
    centers = EducationCenter.objects.all().order_by('name')
    return render(request, 'main/quiz_assign_admin.html', {'centers':centers})


@login_required
def poll_result(request, quiz_id=None):
    this_user = request.user
    quiz = None
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    else:
        message = _("No existeix aquesta prova.")
        go_back_to = "alum_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    if not QuizRun.objects.filter(quiz=quiz).exists():
        message = _("No tens assignada aquesta prova, de manera que no la pots visualitzar.")
        go_back_to = "alum_menu"
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
        go_back_to = "alum_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
    if not QuizRun.objects.filter(quiz=quiz).exists():
        message = _("No tens assignada aquesta prova, de manera que no la pots visualitzar.")
        go_back_to = "alum_menu"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

    return render(request, 'main/quiz_browse.html', {'quiz': quiz})

@login_required
def question_new(request, quiz_id=None):
    quiz = None
    json_answers = None
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    else:
        raise forms.ValidationError("No existeix aquesta prova")
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        json_answers = request.POST.get('answers_json','')
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
    return render(request, 'main/question_new.html', {'form': form, 'quiz': quiz, 'json_answers': json_answers})


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
    return render(request, 'main/question_edit.html', {'form': form, 'question': question, 'json_answers': json_answers})


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
    this_user = request.user
    if quiz_id:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        if this_user.profile.group_teacher.id != quiz.author.id:
            #alum is trying to access a quiz created by someone that is not his tutor
            message = _("Estàs intentant accedir a una prova creada per un professor que no és el teu tutor.")
            go_back_to = "alum_menu"
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
        if done:
            message = _("Aquesta prova està marcada com a finalitzada, o sigui que no la pots modificar. Si vols, la pots repetir.")
            go_back_to = "alum_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

    user_input = QuizRunAnswers.objects.get(question=question, quizrun=quiz_run)

    completed_questions = QuizRunAnswers.objects.filter(quizrun=quiz_run).filter(answered=True).values('question__id')
    completed_questions_list = [a['question__id'] for a in completed_questions]

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
            go_back_to = "alum_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})
        if this_user.profile.group_teacher.id != quiz.author.id:
            #group is trying to start a quiz created by someone that is not his tutor
            message = _("Estàs intentant començar una prova creada per un professor que no és el teu tutor.")
            go_back_to = "alum_menu"
            return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to':go_back_to })
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
        if id_requisite != '-1' and id_requisite != '':
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
            return HttpResponseRedirect('/admin_menu')

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
            return HttpResponseRedirect('/admin_menu')

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
    username = None
    center = ""
    tutor = ""
    centers = EducationCenter.objects.all().order_by('name')
    if pk:
        group = get_object_or_404(User, pk=pk)
        if group.profile and group.profile.group_picture:
            photo_path = group.profile.group_picture.url
        group_password = group.profile.group_password
        group_public_name = group.profile.group_public_name
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
        return render(request, 'main/group_edit.html', {'form': form, 'group_id' : pk, 'photo_path': photo_path, 'group_password': group_password, 'group_public_name': group_public_name, 'username': username, 'centers':centers, 'tutor': tutor, 'center':center })
    elif this_user.profile and this_user.profile.is_teacher:
        return render(request, 'main/group_edit_teacher.html', {'form': form, 'group_id': pk, 'photo_path': photo_path, 'group_password': group_password, 'group_public_name': group_public_name, 'username': username })
    else:
        message = _("Estàs intentant accedir a una pàgina a la que no tens permís.")
        go_back_to = "my_hub"
        return render(request, 'main/invalid_operation.html', {'error_message': message, 'go_back_to': go_back_to})

@login_required
def group_new(request):
    this_user = request.user
    photo_path = None
    centers = EducationCenter.objects.all().order_by('name')
    group_teacher = -1
    group_teacher_center_id = -1
    if request.method == 'POST':
        form = SimplifiedGroupForm(request.POST)
        photo_path = request.POST.get('photo_path')
        group_teacher = request.POST.get('group_teacher')
        group_teacher_center_id = request.POST.get('group_center')
        if this_user.is_superuser:
            tutor = User.objects.get(pk=int(group_teacher))
        elif this_user.profile and this_user.profile.is_teacher:
            tutor = this_user
        if form.is_valid():
            user = form.save()
            user.profile.is_group = True
            user.profile.group_password = form.cleaned_data.get('password1')
            user.profile.group_public_name = form.cleaned_data.get('group_public_name')
            user.profile.group_teacher = tutor
            if photo_path != '':
                copy(str(settings.BASE_DIR) + photo_path, settings.MEDIA_ROOT + "/group_pics/")
                user.profile.group_picture = 'group_pics/' + os.path.basename(photo_path)
            user.save()
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
    return render(request, 'main/test_solutions_teacher.html', {'my_quizzes': my_quizzes})


@api_view(['GET'])
def teachers_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('username','center')
        queryset = User.objects.filter(profile__is_teacher=True)
        field_translation_list = {'username': 'username', 'center': 'profile__teacher_belongs_to__name'}
        sort_translation_list = {'username': 'username', 'center': 'profile__teacher_belongs_to__name'}
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, TeacherSerializer, field_translation_list, sort_translation_list)
        return response


def get_random_row(qs):
    qs_count = qs.count()
    random_index = randint(0, qs_count - 1)
    return qs[random_index]


def generate_random_username_struct():
    color = get_random_row(Word.objects.filter(type='color').order_by('word'))
    adjective = get_random_row(Word.objects.filter(type='adjective').order_by('word'))
    animal = get_random_row(Word.objects.filter(type='animal').order_by('word'))
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

        if id == -1:
            raise ParseError(detail='Quiz run answer id not specified')

        if answer_id == -1:
            answer = None
        else:
            answer = get_object_or_404(Answer, pk=answer_id)

        qra = get_object_or_404(QuizRunAnswers, pk=id)

        qra.chosen_answer = answer
        qra.answered = True
        qra.save()

        done = qra.quizrun.is_done()

        serializer = QuizRunAnswerSerializer(qra)

        response = { "done": done, "data": serializer.data}

        return Response(response)


@api_view(['POST'])
def api_finishquiz(request):
    if request.method == 'POST':
        quizrun_id = request.data.get('id', -1)
        date_finished = datetime.utcnow().replace(tzinfo=pytz.utc)
        if quizrun_id == -1:
            raise ParseError(detail='Quiz id not specified')
        quizrun = get_object_or_404(QuizRun, pk=quizrun_id)
        quizrun.date_finished = date_finished
        if quizrun.quiz.is_test:
            eval_data = quizrun.evaluate()
            quizrun.questions_number = eval_data['questions_number']
            quizrun.questions_right = eval_data['questions_right']
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
def get_random_group_name(request):
    if request.method == 'GET':
        name_struct = generate_random_username_struct()
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
        field_translation_list = {'name': 'name', 'author.username': 'author__username', 'education_center': 'author__profile__teacher_belongs_to__name'}
        sort_translation_list = {'name': 'name', 'author.username': 'author__username', 'education_center': 'author__profile__teacher_belongs_to__name' }
        if this_user.is_superuser:
            queryset = Quiz.objects.select_related('author').all()
        elif this_user.profile.is_teacher:
            queryset = Quiz.objects.select_related('author').filter(author=this_user)
        else:
            pass  # this should not happen
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, QuizSerializer, field_translation_list, sort_translation_list)
        return response


@api_view(['GET'])
def centers_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('name',)
        queryset = EducationCenter.objects.all()
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
        search_field_list = ('username', 'group_public_name', 'group_center', 'group_tutor')
        if this_user.is_superuser:
            queryset = User.objects.filter(profile__is_group=True)
        elif this_user.profile and this_user.profile.is_teacher:
            #groups that contain any of the tutorees
            # tutorized_alums = User.objects.filter(profile__is_alum=True).filter(profile__alum_teacher=this_user)
            # group_ids = []
            # for t_alum in tutorized_alums:
            #     groups = t_alum.profile.alum_in_group.all().values('id')
            #     group_ids += [a['id'] for a in groups]
            # queryset = User.objects.filter(profile__is_group=True).filter(id__in=group_ids)
            queryset = User.objects.filter(profile__is_group=True).filter(profile__group_teacher=this_user)
        else:
            pass #not allowed
        field_translation_list = {'username': 'username', 'group_public_name': 'profile__group_public_name', 'group_center': 'profile__center_string', 'group_tutor':  'profile__group_teacher__username'}
        sort_translation_list = {'username': 'username', 'group_public_name': 'profile__group_public_name', 'group_center': 'profile__center_string', 'group_tutor':  'profile__group_teacher__username'}
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
        queryset = Quiz.objects.filter(author__id=q).order_by('name')
        serializer = QuizComboSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def tutor_combo(request):
    if request.method == 'GET':
        q = request.query_params.get('center_id','')
        if q != '':
            queryset = User.objects.filter(profile__is_teacher=True).filter(profile__teacher_belongs_to__id=q).order_by('username')
        else:
            queryset = User.objects.filter(profile__is_teacher=True).order_by('username')
        serializer = TeacherComboSerializer(queryset, many=True)
        return Response(serializer.data)

@login_required
def uploadpic(request):
    if request.method == 'POST':
        file = request.FILES
        f = request.FILES['camp_foto']
        with open(settings.MEDIA_ROOT + "/tempfiles/" + f.name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        data = {'is_valid': True, 'id':1, 'url':'/media/tempfiles/'+f.name, 'path':settings.MEDIA_ROOT + "/tempfiles/" + f.name}
        return JsonResponse(data)
        # form = PhotoForm(request.POST, request.FILES)
        # if form.is_valid():
        #     foto = form.save(commit=False)
        #     foto.save()
        #     data = {'is_valid': True, 'id': foto.id, 'url': foto.camp_foto.url }
        # else:
        #     data = {'is_valid': False, 'errors': form.errors['foto']}
        # return JsonResponse(data)


class CentersViewSet(viewsets.ModelViewSet):
    queryset = EducationCenter.objects.all()
    serializer_class = EducationCenterSerializer


class QuestionsViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuizzesViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class UserPartialUpdateView(GenericAPIView, UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class EducationCenterPartialUpdateView(GenericAPIView, UpdateModelMixin):
    '''
    You just need to provide the field which is to be modified.
    '''
    queryset = EducationCenter.objects.all()
    serializer_class = EducationCenterSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)