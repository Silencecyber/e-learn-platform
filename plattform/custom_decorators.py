from django.http import HttpResponse
from plattform.models import (Profile, Course,
                              Module, Topic, Quiz)
from django.urls import reverse
from django.shortcuts import redirect,get_object_or_404
import json


# This decorator is for restrictions to modify subscribers
# from other courses
def must_be_allowed_to_modify_subscriber(action):
    if action == 'add':
        def must_be_allowed_to_add_subscriber(func):
            def wrapper(*args, **kwargs):

                request = args[1]
                user = request.user
                course = get_object_or_404(Course,pk=args[0].kwargs.get('pk'))

                if user == course.author or user.is_staff:
                    return func(*args, **kwargs)
                else:
                    return HttpResponse('Forbidden!')

            return wrapper

        return must_be_allowed_to_add_subscriber

    elif action == 'delete':
        def must_be_allowed_to_delete_subscriber(func):
            def wrapper(*args, **kwargs):

                request = args[1]
                user = request.user
                if request.method == 'GET':
                    course = get_object_or_404(Course,pk=args[0].kwargs.get('pk'))
                else:
                    course = get_object_or_404(Course,pk=request.GET.get('course'))
                if user == course.author or user.is_staff:
                    return func(*args, **kwargs)
                else:
                    return HttpResponse('Forbidden!')

            return wrapper

        return must_be_allowed_to_delete_subscriber


# These are decorators to restrict teachers to modify others' courses
def must_be_author(related_to, action):
    if related_to == 'course':
        if action in ['edit', 'delete']:
            def must_be_course_author_or_admin(func):
                def wrapper(*args, **kwargs):
                    course_id = args[0].kwargs.get('pk')
                    request = args[1]
                    user = request.user
                    course_author = get_object_or_404(Course,pk=course_id).author

                    # check if user is an author of course or is an admin
                    if user == course_author or user.is_staff:
                        return func(*args, **kwargs)
                    else:
                        return HttpResponse('Forbidden!')

                return wrapper

            return must_be_course_author_or_admin


    elif related_to == 'module':

        if action == 'add':
            def must_be_module_author_or_admin(func):
                def wrapper(*args, **kwargs):
                    request = args[1]
                    course = request.POST.get('course')
                    user = request.user
                    course_author = get_object_or_404(Course,pk=course).author

                    if user == course_author or user.is_staff:
                        return func(*args, **kwargs)
                    else:
                        return HttpResponse('Forbidden!')

                return wrapper

            return must_be_module_author_or_admin
        elif action in ['edit', 'delete']:
            def must_be_module_author_or_admin(func):
                def wrapper(*args, **kwargs):
                    request = args[1]
                    module_id = args[0].kwargs.get('pk')
                    module = get_object_or_404(Module,pk=module_id)
                    course = module.course

                    user = request.user
                    course_author = get_object_or_404(Course,pk=course.id).author

                    if user == course_author or user.is_staff:
                        return func(*args, **kwargs)
                    else:
                        return HttpResponse('Forbidden!')

                return wrapper

            return must_be_module_author_or_admin

    elif related_to == 'topic':

        if action == 'add':
            def must_be_topic_author_or_admin(func):
                def wrapper(*args, **kwargs):
                    request = args[1]
                    module_id = request.POST.get('module')
                    module = get_object_or_404(Module,pk=module_id)
                    course_author = module.course.author
                    user = request.user

                    if user == course_author or user.is_staff:
                        return func(*args, **kwargs)
                    else:
                        return HttpResponse('Forbidden!')

                return wrapper

            return must_be_topic_author_or_admin
        elif action == 'edit':
            def must_be_topic_author_or_admin(func):
                def wrapper(*args, **kwargs):
                    request = args[1]
                    user = request.user
                    topic_id = args[0].kwargs.get('pk')
                    topic = get_object_or_404(Topic,pk=topic_id)

                    module = topic.module
                    course = module.course

                    if (user != course.author) and not user.is_staff:
                        return HttpResponse('Forbidden!')

                    if request.method == 'POST':

                        module_id_from_user = request.POST.get('module')
                        module_from_user = get_object_or_404(Module,pk=module_id_from_user)
                        course_author = module_from_user.course.author

                        if user == course_author or user.is_staff:
                            return func(*args, **kwargs)
                        else:
                            return HttpResponse('Forbidden!')
                    else:
                        return func(*args, **kwargs)

                return wrapper

            return must_be_topic_author_or_admin

        elif action == 'delete':
            def must_be_topic_author_or_admin(func):
                def wrapper(*args, **kwargs):
                    request = args[1]
                    user = request.user
                    topic_id = args[0].kwargs.get('pk')
                    topic = get_object_or_404(Topic,pk=topic_id)

                    module = topic.module
                    course = module.course

                    if (user != course.author) and not user.is_staff:
                        return HttpResponse('Forbidden!')

                    else:
                        return func(*args, **kwargs)

                return wrapper

            return must_be_topic_author_or_admin

    elif related_to == 'quiz':
        if action == 'add':
            def must_be_quiz_author_or_admin(func):
                def wrapper(*args, **kwargs):
                    request = args[1]
                    if request.method == 'GET':
                        module_id = request.GET.get('module_id')
                    else:
                        data = dict(json.loads(request.body))
                        module_id = data['module_id']
                    module = get_object_or_404(Module,pk=module_id)
                    course = module.course
                    user = request.user

                    if course.author == user or user.is_staff:
                        return func(*args, **kwargs)
                    else:
                        return HttpResponse('Forbidden!')

                return wrapper

            return must_be_quiz_author_or_admin
        if action in ['edit', 'delete']:
            def must_be_quiz_author_or_admin(func):
                def wrapper(*args, **kwargs):
                    request = args[1]
                    quiz_id = args[0].kwargs.get('quiz_id')
                    quiz = get_object_or_404(Quiz,pk=quiz_id)
                    course = quiz.course
                    user = request.user

                    if user == course.author or user.is_staff:
                        return func(*args, **kwargs)
                    else:
                        return HttpResponse('Forbidden')

                return wrapper

            return must_be_quiz_author_or_admin


# decorator for a student access restriction
def must_be_teacher(func):
    def wrapper(*args, **kwargs):

        request = args[1]
        is_teacher = get_object_or_404(Profile,user=request.user.id).is_teacher
        if not is_teacher:
            return redirect(reverse('plattform:home'))
        else:
            return func(*args, **kwargs)

    return wrapper
