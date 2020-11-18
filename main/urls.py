from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'centers', views.CentersViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/',include(router.urls)),
    path('teacher_menu', views.teacher_menu, name='teacher_menu'),
    path('admin_menu', views.admin_menu, name='admin_menu'),
    path('quiz/new/', views.quiz_new, name='quiz_new'),
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
    path('alum/datatablelist/', views.alum_datatable_list, name='alum_datatable_list'),
    path('group/new/', views.group_new, name='group_new'),
    path('group/list/', views.group_list, name='group_list'),
    path('group/update/<int:pk>/', views.group_update, name='group_update'),
    path('group/update/', views.group_update, name='group_update_no_id'),
    path('group/search/', views.group_search, name='group_search'),
    path('group/datatablelist/', views.group_datatable_list, name='group_datatable_list'),
    path('user/update-partial/<int:pk>/', views.UserPartialUpdateView.as_view(), name='user_partial_update'),
    path('user/update-partial/', views.UserPartialUpdateView.as_view(), name='user_partial_update'),
    path('user/password/change/', views.change_password, name='change_password'),
    path('user/password/change/<int:user_id>/', views.change_password, name='change_password'),
    path('api/group_name/', views.get_random_group_name, name='get_random_group_name'),
    path('uploadpic', views.uploadpic, name="uploadpic"),
]
