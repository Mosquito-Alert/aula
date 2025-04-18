from django.conf import settings
from django.conf import settings
from django.conf.urls.static import static
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
    path('i18n/', include('django.conf.urls.i18n')),
    path('my_hub/', views.my_hub, name='my_hub'),
    path('api/',include(router.urls)),
    path('teacher_menu', views.teacher_menu, name='teacher_menu'),
    path('admin_menu', views.admin_menu, name='admin_menu'),
    #path('alum_menu', views.alum_menu, name='alum_menu'),
    path('group_menu', views.group_menu, name='group_menu'),
    path('consent_form', views.consent_form, name='consent_form'),
    path('quiz/browse/<int:quiz_id>/', views.quiz_browse, name='quiz_browse'),
    path('quiz/browse/', views.quiz_browse, name='quiz_browse_no_id'),
    path('quiz/poll_result/<int:quiz_id>/', views.poll_result, name='poll_result'),
    path('quiz/teacher_open_result/<int:quiz_id>/', views.teacher_open_result, name='teacher_open_result'),
    # This does the same as /reports/poll_center_or_group
    # it's not deleted because the implementation uses custom template tags, kept as reference
    #path('quiz/poll_result/<int:quiz_id>/<int:group_id>/', views.poll_result_group, name='poll_result_group'),
    path('quiz/new/', views.quiz_new, name='quiz_new'),
    path('quiz/list/', views.quiz_list, name='quiz_list'),
    path('quiz/update/', views.quiz_update, name='quiz_update_no_id'),
    path('quiz/update/<int:pk>/', views.quiz_update, name='quiz_update'),
    path('quiz/pdf/<int:quiz_id>/', views.quiz_pdf, name='quiz_pdf'),
    path('quiz/datatablelist/', views.quiz_datatable_list, name='quiz_datatable_list'),
    path('quiz/start/<int:pk>/', views.quiz_start, name='quiz_take_splash'),
    path('quiz/take/<int:quiz_id>/<int:question_number>/', views.quiz_take, name='quiz_take'),
    path('quiz/take/<int:quiz_id>/<int:question_number>/<int:run_id>/', views.quiz_take, name='quiz_take'),
    path('quiz/take_upload/<int:quiz_id>/<int:run_id>/', views.quiz_take_upload, name='quiz_take_upload'),
    path('quiz/upload_link/<int:quiz_id>/', views.quiz_upload_link, name='quiz_upload_link'),
    path('quiz/take/endsummary/<int:quizrun_id>/', views.quiz_take_endsummary, name='quiz_take_endsummary'),
    path('quiz/assign_admin/', views.quiz_assign_admin, name='quiz_assign_admin'),
    path('quiz/search/', views.quiz_search, name='quiz_search'),
    path('quiz/copy/', views.quiz_copy, name='quiz_copy'),
    path('quiz/solutions/', views.quiz_solutions, name='quiz_solutions'),
    path('quiz/open_answer_results/', views.open_answer_results, name='open_answer_results'),
    path('quiz/open_answer_results/<str:slug>/', views.open_answer_results_class, name='open_answer_results_class'),
    path('quiz/open_answer/update/<int:quizcorrection_id>', views.open_answer_edit, name='open_answer_edit'),
    path('quiz/open_answer/new/<int:quizrun_id>', views.open_answer_new, name='open_answer_new'),
    path('quiz/open_answer/detail/<int:quizcorrection_id>', views.open_answer_detail, name='open_answer_detail'),
    path('quiz/open_answer_teacher/detail/<int:quizrun_id>', views.open_answer_teacher_detail, name='open_answer_teacher_detail'),
    path('question/new/<int:quiz_id>/', views.question_new, name='question_new'),
    path('question/new/', views.question_new, name='question_new'),
    path('question_link/new/<int:quiz_id>/', views.question_link_new, name='question_link_new'),
    path('question_link/new/', views.question_link_new, name='question_link_new'),
    path('question_poll/new/<int:quiz_id>/', views.question_poll_new, name='question_poll_new'),
    path('question_poll/new/', views.question_poll_new, name='question_poll_new'),
    path('question_open/new/<int:quiz_id>/', views.question_open_new, name='question_open_new'),
    path('question_open/new/', views.question_open_new, name='question_open_new'),
    path('question_open/update/<int:pk>/', views.question_open_update, name='question_open_update'),
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
    path('teacher/polls/list/', views.teacher_polls, name='teacher_polls'),
    path('teacher/update/<int:pk>/', views.teacher_update, name='teacher_update'),
    path('teacher/update/', views.teacher_update, name='teacher_update_no_id'),
    path('teacher/datatablelist/', views.teachers_datatable_list, name='teachers_datatable_list'),
    path('center/new/', views.center_new, name='center_new'),
    path('center/list/', views.center_list, name='center_list'),
    path('center/map/', views.center_map, name='center_map'),
    path('center/update/<int:pk>/', views.center_update, name='center_update'),
    path('center/update/', views.center_update, name='center_update_no_id'),
    path('center/datatablelist/', views.centers_datatable_list, name='centers_datatable_list'),
    path('center/update-partial/<int:pk>/', views.EducationCenterPartialUpdateView.as_view(), name='center_partial_update'),
    path('reports/', views.reports, name='reports'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/datatablelist/', views.notifications_datatable_list, name='notifications_datatable_list'),
    path('reports/poll_center_or_group/<int:poll_id>/<int:center_id>/<int:group_id>/', views.reports_poll_center_or_group, name='reports_poll_center_or_group'),
    path('reports/poll_center_or_group/<int:poll_id>/<int:center_id>/', views.reports_poll_center_or_group, name='reports_poll_center_or_group'),
    path('reports/poll_class/<int:poll_id>/<int:teacher_id>/<str:slug>/', views.reports_poll_class, name='reports_poll_class'),
    path('reports/teacher_poll_center/<int:poll_id>/', views.reports_teacher_poll_center, name='teacher_poll_center'),
    path('reports/teacher_poll_center/<int:poll_id>/<int:center_id>/', views.reports_teacher_poll_center, name='teacher_poll_center'),
    path('reports/center_progress/<int:center_id>/', views.center_progress, name='center_progress'),
    path('reports/center_progress/<int:center_id>/<str:slug>/', views.center_progress_class, name='center_progress_class'),
    path('reports/teacher_poll_comments/', views.teacher_poll_comments, name='teacher_poll_comments'),
    path('reports/teacher_poll_comments/<int:poll_id>/<int:center_id>/', views.teacher_poll_comments, name='teacher_poll_comments'),
    path('reports/n_pupils_distribution_center/<int:center_id>/', views.n_pupils_distribution_center, name='n_pupils_distribution_center'),
    path('reports/tabular_report/<int:quiz_id>/', views.tabular_report, name='tabular_report'),
    path('reports/project_outline/', views.project_outline, name='project_outline'),
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
    path('internalnotification/update-partial/<int:pk>/', views.InternalNotificationUpdateView.as_view(), name='notif_partial_update'),
    path('internalnotification/update-partial/', views.InternalNotificationUpdateView.as_view(), name='notif_partial_update'),
    path('user/update-partial/<int:pk>/', views.UserPartialUpdateView.as_view(), name='user_partial_update'),
    path('user/update-partial/', views.UserPartialUpdateView.as_view(), name='user_partial_update'),
    path('user/password/change/', views.change_password, name='change_password'),
    path('user/password/change/<int:user_id>/', views.change_password, name='change_password'),
    path('credits/', views.credits, name='credits'),
    path('api/group_name/', views.get_random_group_name, name='get_random_group_name'),
    path('api/group_name/<str:locale>/', views.get_random_group_name, name='get_random_group_name'),
    path('api/startrun/', views.api_startrun, name='api_startrun'),
    path('api/writeanswer/', views.api_writeanswer, name='api_writeanswer'),
    path('api/finishquiz/', views.api_finishquiz, name='api_finishquiz'),
    path('api/copy_test/', views.copy_test, name='api_copytest'),
    path('uploadpic', views.uploadpic, name="uploadpic"),
    path('uploadfile', views.uploadfile, name="uploadfile"),
    path('uploadquestionpic', views.upload_question_pic, name="upload_question_pic"),
    path('api/tutor_combo/', views.tutor_combo, name="tutor_combo"),
    path('api/group_combo/', views.group_combo, name="group_combo"),
    path('api/complete_upload/', views.complete_upload, name="complete_upload"),
    path('api/toggle_check/', views.toggle_check, name="toggle_check"),
    path('api/auth_material/', views.auth_material, name="auth_material"),
    path('api/requirements_combo/', views.requirements_combo, name="requirements_combo"),
    path('api/toggle_campaign_active/', views.toggle_campaign_active, name="toggle_campaign_active"),
    path('makepdf', views.group_credentials_list, name='generatePDF'),
    path('quiz/graphic_results/<int:idQuizz>/', views.quiz_graphic_results, name='quiz_graphic_results'),
    path('quiz/results/', views.quiz_results, name='quiz_results'),
    path('quiz/datatableresults/', views.quiz_datatable_results, name='quiz_datatable_results'),
    path('quiz/test_result/<int:quiz_id>/', views.test_result, name='test_result'),
    path('quiz/test_result/<int:quiz_id>/<str:slug>/', views.test_result_class, name='test_result_class'),
    path('upload_file/solutions/', views.upload_file_solutions, name='upload_file_solutions'),
    path('upload_file/solutions/<str:slug>/', views.upload_file_solutions_class, name='upload_file_solutions_class'),
    path('upload_file/admin_board/', views.upload_admin_board, name='upload_admin_board'),
    path('upload_file/admin_board_csv/', views.upload_admin_board_csv, name='upload_admin_board_csv'),
    path('upload_file/download/<int:quizrunanswer_id>/', views.named_download, name='named_download'),
    path('tinymce/', include('tinymce.urls')),
    path('quiz/test_result_grouplist/<int:quiz_id>/<int:group_id>/', views.quizrun_group_list, name='quizrun_group_list'),
    path('quizrun/delete/<int:quizrun_id>/', views.delete_quizrun, name='delete_quizrun'),
    path('quiz/test_result/<int:quiz_id>/<int:group_id>/detail/', views.test_results_detail_view, name='test_results_detail_view'),
    path('campaign/new/', views.campaign_new, name='campaign_new'),
    path('campaign/list/', views.campaign_list, name='campaign_list'),
    path('campaign/update/<int:pk>/', views.campaign_update, name='campaign_update'),
    path('campaign/update/', views.campaign_update, name='campaign_update_no_id'),
    path('campaign/datatablelist/', views.campaign_datatable_list, name='campaign_datatable_list'),
    #path('map/', views.map, name='map'),
    path('map/', views.map_campaign_year, name='map_campaign_year'),
    #path('map/<int:campaign>/', views.map_campaign, name='map_campaign'),
    path('map/<int:year>/', views.map_campaign_year, name='map_campaign_year'),
    path('api/center_info/', views.center_info, name='center_info' ),
    path('api/quizzes_campaign/', views.quizzes_campaign, name='quizzes_campaign' ),
    path('api/center_info/<int:pk>/', views.center_info, name='center_info' ),
    path('api/delete_material/<int:pk>/', views.delete_material, name='delete_material' ),
    path('api/center_bs/<str:hash>/', views.center_bs, name='center_bs' ),
    path('api/visited_consent/', views.visited_consent, name='visited_consent' ),
    path('api/input_consent/', views.input_consent, name='input_consent' ),
]
