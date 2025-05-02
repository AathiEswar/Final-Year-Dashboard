from django.urls import path, re_path , include
from django.conf import settings
from django.views.static import serve

from Login import views as login_views
from Profile import views as profile_views
from Dashboard import views as dashboard_views
from Departments import views as department_views
from Users import views as user_views
from Projects import views as project_views
from Budgets import views as budget_views
from Tasks import views as task_views
from Department_Head import views as department_head_views
from Employee import views as employee_views
from ChatBot import views as chatbot_views
from ChatBotEmployee import views as chatbot_employee_views
from ChatBotProjectManager import views as chatbot_projectmanager_views

urlpatterns = [
    path('login', login_views.login),
    path('logout', login_views.logout),
    path('department-head/logout', login_views.logout),
    path('employee/logout', login_views.logout),
    path('', dashboard_views.index),
    path('profile', profile_views.index),
    path('department', department_views.index),
    path('department/add', department_views.add),
    path('department/edit/<int:id>', department_views.edit),
    path('user', user_views.index),
    path('user/add', user_views.add),
    path('user/edit/<int:id>', user_views.edit),
    path('project', project_views.index),
    path('project/add', project_views.add),
    path('project/edit/<int:id>', project_views.edit),
    path('budget', budget_views.index),
    path('budget/add', budget_views.add),
    path('budget/edit/<int:id>', budget_views.edit),
    path('task', task_views.index),
    path('task/add', task_views.add),
    path('generate-description' , task_views.generate_description), 
    path('task/edit/<int:id>', task_views.edit),
    path('department-head/dashboard', department_head_views.dashboard_index),
    path('department-head/profile', department_head_views.profile_index),
    path('department-head/project', department_head_views.project_index),
    path('department-head/user', department_head_views.user_index),
    path('department-head/user/add', department_head_views.user_add),
    path('department-head/user/edit/<int:id>', department_head_views.user_edit),
    path('department-head/task', department_head_views.task_index),
    path('department-head/task/<int:id>', department_head_views.task_index_user),
    path('department-head/task/add', department_head_views.task_add),
    path('department-head/task/edit/<int:id>', department_head_views.task_edit),
    path('department-head/generate-description' , department_head_views.generate_description), 
    path('department-head/api/', include('ChatBotProjectManager.urls')),  
    path('employee/dashboard', employee_views.dashboard_index),
    path('employee/profile', employee_views.profile_index),
    path('employee/task', employee_views.task_index),
    path('employee/task/edit/<int:id>', employee_views.task_edit),
    path('employee/api/', include('ChatBotEmployee.urls')),  
    path('api/', include('ChatBot.urls')),  
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
