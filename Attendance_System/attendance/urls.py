from django.contrib import admin
from django.urls import path
from database import views
from django.conf.urls.static import static
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('signup/', views.signup, name="signup"),
    path('student/', views.student_signup, name="student_signup"),
    path('faculty/', views.faculty_signup, name="faculty_signup"),
    path('<str:name>/<str:isface>/', views.selectdegree, name="selectdegree"),
    path('<str:name>/<str:isface>/<str:degree>/', views.selectyear, name="selectyear"),
    path('<str:name>/<str:isface>/<str:degree>/<int:year>/', views.selectbranch, name="selectbranch"),
    path('<str:name>/<str:isface>/<str:degree>/<int:year>/<str:branch>/', views.selectcourse, name="selectcourse"),
    path('<str:name>/<str:isface>/<str:degree>/<int:year>/<str:branch>/<str:course>/home/', views.home, name="home"),
    path('<str:name>/<str:isface>/<str:degree>/<int:year>/<str:branch>/<str:course>/enroll/', views.enroll, name="enroll"),
    path('<str:name>/<str:isface>/<str:degree>/<int:year>/<str:branch>/<str:course>/viewattendance/', views.viewattendance, name="viewattendance"),
    path('download/<str:file_name>', serve, {'document_root': settings.STATIC_ROOT}),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
