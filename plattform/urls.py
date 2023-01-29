from django.urls import path
import plattform.views as view
app_name='plattform'

urlpatterns = [
    path('login',view.LoginView.as_view(),name='login'),
    path('home',view.HomeView.as_view(),name='home'),
    path('logout',view.LogoutView.as_view(),name='logout'),
    path('students',view.StudentsView.as_view(),name='students'),
    path('create/student',view.StudentCreateView.as_view(),name='create_student'),
    path('delete/student/<int:pk>',view.StudentDeleteView.as_view(),name='delete_student'),
    path('course/<int:pk>',view.CourseDetailView.as_view(),name='course_detail'),
    path('topic/<int:pk>',view.TopicDetailView.as_view(),name='topic_detail'),
    path('courses',view.CoursesView.as_view(),name='courses'),
    path('create/course',view.CourseCreateView.as_view(),name='create_course'),
    path('edit/course/<int:pk>',view.CourseEditView.as_view(),name='edit_course'),
    path('delete/course/<int:pk>',view.CourseDeleteView.as_view(),name='delete_course'),
    path('add/module/',view.ModuleAddView.as_view(),name='add_module'),
    path('edit/module/<int:pk>',view.ModuleEditView.as_view(),name='edit_module'),
    path('delete/module/<int:pk>',view.ModuleDeleteView.as_view(),name='delete_module'),
    path('add/topic/',view.TopicAddView.as_view(),name='add_topic'),
    path('edit/topic/<int:pk>',view.TopicEditView.as_view(),name='edit_topic'),
    path('delete/topic/<int:pk>',view.TopicDeleteView.as_view(),name='delete_topic'),
    path('course/subscribers/<int:pk>',view.CourseSubscribersView.as_view(),name='course_subscribers'),
    path('course/subscriber/delete',view.SubscriberDeleteView.as_view(),name='delete_subscriber'),
    path('course/subscribers/<int:pk>/add',view.SubscriberAddView.as_view(),name='add_subscriber'),
    path('profile/',view.PersonalProfileView.as_view(),name='profile'),
    path('profile/edit',view.ProfileEditView.as_view(),name='profile_edit'),
    path('profile/change/password',view.ChangeSelfPasswordView.as_view(),name='change_self_password'),
    path('profile/<int:pk>',view.OtherProfileView.as_view(),name='other_profile'),
    path('course/<int:pk>/classmates',view.ClassmatesView.as_view(),name='classmates'),
    path('module/<int:module_id>/quiz/<int:quiz_id>',view.QuizView.as_view(),name='quiz'),
    path('api/check_results/',view.CheckResultsView.as_view(),name='check_results'),
    path('create/quiz/',view.CreateQuizView.as_view(),name='create_quiz'),
    path('edit/quiz/<int:quiz_id>',view.EditQuizView.as_view(),name='edit_quiz'),
    path('remove/quiz/<int:quiz_id>',view.DeleteQuizView.as_view(),name='delete_quiz'),
    path('student/change_password/<int:user_id>',view.ChangePasswordView.as_view(),name='change_password'),
    path('course/<int:course_id>/gradebook',view.GradebookView.as_view(),name='gradebook'),
    path('create/teacher',view.CreateTeacherView.as_view(),name='create_teacher'),
    path('teachers',view.TeachersView.as_view(),name='teachers'),
    path('delete/teacher/<int:teacher_id>',view.DeleteTeacherView.as_view(),name='delete_teacher')
]