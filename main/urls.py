from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'centers', views.CentersViewSet)
router.register(r'questions', views.QuestionsViewSet, basename="questions")
router.register(r'quizzes', views.QuizzesViewSet, basename="quizzes")

urlpatterns = [
    path('', views.index, name='index'),
    path('my_hub/', views.my_hub, name='my_hub'),
    path('api/',include(router.urls)),
    path('teacher_menu', views.teacher_menu, name='teacher_menu'),
    path('admin_menu', views.admin_menu, name='admin_menu'),
    #path('alum_menu', views.alum_menu, name='alum_menu'),
    path('group_menu', views.group_menu, name='group_menu'),
    path('quiz/browse/<int:quiz_id>/', views.quiz_browse, name='quiz_browse'),
    path('quiz/poll_result/<int:quiz_id>/', views.poll_result, name='poll_result'),
    path('quiz/new/', views.quiz_new, name='quiz_new'),
    path('quiz/list/', views.quiz_list, name='quiz_list'),
    path('quiz/update/', views.quiz_update, name='quiz_update_no_id'),
    path('quiz/update/<int:pk>/', views.quiz_update, name='quiz_update'),
    path('quiz/datatablelist/', views.quiz_datatable_list, name='quiz_datatable_list'),
    path('quiz/start/<int:pk>/', views.quiz_start, name='quiz_take_splash'),
    path('quiz/take/<int:quiz_id>/<int:question_number>/', views.quiz_take, name='quiz_take'),
    path('quiz/take/<int:quiz_id>/<int:question_number>/<int:run_id>/', views.quiz_take, name='quiz_take'),
    path('quiz/take_upload/<int:quiz_id>/<int:run_id>/', views.quiz_take_upload, name='quiz_take_upload'),
    path('quiz/take/endsummary/<int:quizrun_id>/', views.quiz_take_endsummary, name='quiz_take_endsummary'),
    path('quiz/assign_admin/', views.quiz_assign_admin, name='quiz_assign_admin'),
    path('quiz/search/', views.quiz_search, name='quiz_search'),
    path('quiz/solutions/', views.quiz_solutions, name='quiz_solutions'),
    path('question/new/<int:quiz_id>/', views.question_new, name='question_new'),
    path('question/new/', views.question_new, name='question_new'),
    path('question_link/new/<int:quiz_id>/', views.question_link_new, name='question_link_new'),
    path('question_link/new/', views.question_link_new, name='question_link_new'),
    path('question_poll/new/<int:quiz_id>/', views.question_poll_new, name='question_poll_new'),
    path('question_poll/new/', views.question_poll_new, name='question_poll_new'),
    path('question/update/', views.question_update, name='question_update_no_id'),
    path('question/update/<int:pk>/', views.question_update, name='question_update'),
    path('question_poll/update/', views.question_poll_update, name='question_poll_update_no_id'),
    path('question_poll/update/<int:pk>/', views.question_poll_update, name='question_poll_update'),
    path('question_link/update/', views.question_link_update, name='question_link_update_no_id'),
    path('question_link/update/<int:pk>/', views.question_link_update, name='question_link_update'),
    path('question_upload/new/', views.question_upload_new, name='question_upload_new'),
    path('question_upload/new/<int:quiz_id>/', views.question_upload_new, name='question_upload_new'),
    path('question_upload/update/', views.question_upload_update, name='question_upload_update'),
    path('question_upload/update/<int:pk>/', views.question_upload_update, name='question_upload_update'),
    path('teacher/new/', views.teacher_new, name='teacher_new'),
    path('teacher/list/', views.teacher_list, name='teacher_list'),
    path('teacher/update/<int:pk>/', views.teacher_update, name='teacher_update'),
    path('teacher/update/', views.teacher_update, name='teacher_update_no_id'),
    path('teacher/datatablelist/', views.teachers_datatable_list, name='teachers_datatable_list'),
    path('center/new/', views.center_new, name='center_new'),
    path('center/list/', views.center_list, name='center_list'),
    path('center/update/<int:pk>/', views.center_update, name='center_update'),
    path('center/update/', views.center_update, name='center_update_no_id'),
    path('center/datatablelist/', views.centers_datatable_list, name='centers_datatable_list'),
    path('center/update-partial/<int:pk>/', views.EducationCenterPartialUpdateView.as_view(), name='center_partial_update'),
    path('alum/new/', views.alum_new, name='alum_new'),
    path('alum/list/', views.alum_list, name='alum_list'),
    path('alum/update/<int:pk>/', views.alum_update, name='alum_update'),
    path('alum/update/', views.alum_update, name='alum_update_no_id'),
    path('alum/search/', views.alum_search, name='alum_search'),
    path('alum/datatablelist/', views.alum_datatable_list, name='alum_datatable_list'),
    path('group/new/', views.group_new, name='group_new'),
    path('group/list/', views.group_list, name='group_list'),
    path('group/list/pdf/', views.group_list_pdf, name='group_list_pdf'),
    path('group/update/<int:pk>/', views.group_update, name='group_update'),
    path('group/update/', views.group_update, name='group_update_no_id'),
    path('group/search/', views.group_search, name='group_search'),
    path('group/datatablelist/', views.group_datatable_list, name='group_datatable_list'),
    path('user/update-partial/<int:pk>/', views.UserPartialUpdateView.as_view(), name='user_partial_update'),
    path('user/update-partial/', views.UserPartialUpdateView.as_view(), name='user_partial_update'),
    path('user/password/change/', views.change_password, name='change_password'),
    path('user/password/change/<int:user_id>/', views.change_password, name='change_password'),
    path('credits/', views.credits, name='credits'),
    path('api/group_name/', views.get_random_group_name, name='get_random_group_name'),
    path('api/startrun/', views.api_startrun, name='api_startrun'),
    path('api/writeanswer/', views.api_writeanswer, name='api_writeanswer'),
    path('api/finishquiz/', views.api_finishquiz, name='api_finishquiz'),
    path('uploadpic', views.uploadpic, name="uploadpic"),
    path('uploadfile', views.uploadfile, name="uploadfile"),
    path('uploadquestionpic', views.upload_question_pic, name="upload_question_pic"),
    path('api/tutor_combo/', views.tutor_combo, name="tutor_combo"),
    path('api/complete_upload/', views.complete_upload, name="complete_upload"),
    path('api/requirements_combo/', views.requirements_combo, name="requirements_combo"),
    path('makepdf', views.group_credentials_list, name='generatePDF'),
    path('quiz/graphic_results/<int:idQuizz>/', views.quiz_graphic_results, name='quiz_graphic_results'),
]
