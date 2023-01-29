from django.shortcuts import render, redirect, get_object_or_404
import random
from django.db.models import Count
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
import json
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from plattform.models import (
    Profile,
    Course,
    Subscriber,
    Module,
    Topic,
    Quiz,
    Question,
    Answer,
    Got,
    QuizResult,
)
from plattform.forms import CourseForm, ModuleForm, TopicForm, ProfileForm

from heapq import nlargest

from plattform.custom_decorators import (
    must_be_teacher,
    must_be_author,
    must_be_allowed_to_modify_subscriber,
)


class LoginView(View):
    def get(self, request):
        return render(request, "plattform/login.html")

    def post(self, request):
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect(reverse("plattform:home"))
        else:
            context = {
                "error": "Wrong credentials! Try again or ask a manager for help."
            }
            return render(request, "plattform/login.html", context)


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect(reverse("about"))


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        is_teacher = Profile.objects.get(user=request.user.id).is_teacher

        if is_teacher:

            return render(request, "plattform/home_teacher.html")

        else:
            context = {}
            courses = []

            for course in Subscriber.objects.filter(user=request.user.id):
                course_data = course.course
                data = {"course": course.course}

                description = course_data.description

                data["description"] = description
                courses.append(data)

            for course in courses:
                total_progress = 0
                user_progress = 0
                topic_count = 0
                got_counter = 0
                subscriber = Subscriber.objects.get(
                    course=course["course"], user=request.user
                )
                modules = Module.objects.filter(course=course["course"])
                quizes_data = []
                for module in modules:
                    topics = Topic.objects.filter(module=module)
                    total_progress += len(topics)
                    quizes = Quiz.objects.filter(module=module)
                    total_progress += len(quizes) * 100

                    for quiz in quizes:
                        quiz_name = quiz.name
                        quiz_result, created = QuizResult.objects.get_or_create(
                            quiz=quiz,
                            subscriber=subscriber,
                            course=course["course"],
                            module=module,
                        )

                        user_progress += quiz_result.result
                        quizes_data.append(
                            {"quiz_name": quiz_name, "quiz_result": quiz_result}
                        )

                    for topic in topics:
                        got, created = Got.objects.get_or_create(subscriber=subscriber, topic=topic)

                        topic_count += 1
                        if got.got:
                            got_counter += 1
                user_progress += got_counter
                course["total_progress"] = total_progress
                course["user_progress"] = user_progress
                try:
                    course["course_progress"] = round(
                        (user_progress * 100) / total_progress
                    )
                except ZeroDivisionError:
                    course["course_progress"] = 0

            context["courses"] = courses

            return render(request, "plattform/home_student.html", context)

    @must_be_teacher
    def post(self, request):

        context = {}
        courses = Course.objects.all()
        courses_len = len(courses)
        get_top_courses = 5

        get_top_quizes_amount = 5

        get_top_topics_amount = 5
        bigger_the_course_limit = False
        bigger_the_topics_limit = False
        bigger_the_quiz_limit = False

        # Get top  courses
        subs = (
            Subscriber.objects.values("course")
            .annotate(total=Count("course"))
            .order_by("-total")
        )
        """
             Raw SQL equivalent

             SELECT course_id,COUNT(*) as total
             FROM plattform_subscriber
             GROUP BY course_id
             ORDER BY  total DESC
        """

        if courses_len > get_top_courses:
            subs = subs[:get_top_courses]
            bigger_the_course_limit = True

        courses_popularity = []
        for course in subs:
            name = Course.objects.get(pk=course["course"]).name
            y = course["total"]
            courses_popularity.append({"name": name, "y": y})

        quizes = (
            Quiz.objects.values("course")
            .annotate(total=Count("course"))
            .order_by("-total")
        )

        """
           Raw SQL equivalent

           SELECT course_id,COUNT(*) as total
           FROM plattform_quiz
           GROUP BY course_id
           ORDER BY  total DESC
        """

        if courses_len > get_top_quizes_amount:
            quizes = quizes[:get_top_quizes_amount]
            bigger_the_quiz_limit = True

        quizes_amount = []
        for quizes_set in quizes:
            name = Course.objects.get(pk=quizes_set["course"]).name
            y = quizes_set["total"]
            quizes_amount.append({"name": name, "y": y})

        topics_courses_count = []
        topics_amount = []
        for course in courses:
            course_name = course.name
            topics_count = 0

            for module in course.modules.all():
                topics_count += module.topics.count()
            topics_amount.append({"name": course_name, "y": topics_count})

            topics_courses_count.append(topics_count)

        if courses_len > get_top_topics_amount:
            topics_amount = nlargest(
                get_top_topics_amount, topics_amount, key=lambda item: item["y"]
            )
            bigger_the_topics_limit = True
        admin_profile = User.objects.get(is_staff=True)

        students_number = len(Profile.objects.filter(is_teacher=False))
        # getting teachers number, except admin user, who is a "teacher" but only for deploying purposes
        teachers_number = len(
            Profile.objects.filter(is_teacher=True).exclude(user=admin_profile)
        )

        context["courses_popularity"] = courses_popularity
        context["courses_number"] = courses_len
        context["students_number"] = students_number
        context["teachers_number"] = teachers_number
        context["topics_amount"] = topics_amount
        context["quizes_amount"] = quizes_amount
        context["bigger_the_course_limit"] = bigger_the_course_limit
        context["course_top_limit"] = get_top_courses
        context["bigger_the_quiz_limit"] = bigger_the_quiz_limit
        context["quiz_top_limit"] = get_top_quizes_amount
        context["topics_top_limit"] = get_top_topics_amount
        context["bigger_the_topic_limit"] = bigger_the_topics_limit

        return JsonResponse(context)


class StudentsView(LoginRequiredMixin, View):
    @must_be_teacher
    def get(self, request):
        students = Profile.objects.all().filter(is_teacher=False).order_by("user")
        remainder = len(students) / 10
        students_count = len(students)

        if remainder < 1:
            pages_count = 1
        if remainder % 1 != 0:
            pages_count = int(remainder) + 1
        else:
            pages_count = int(remainder)

        if not request.GET.get("page"):
            current_page = 1
            if students_count > 10:
                students = students[:10]

        else:
            page = int(request.GET.get("page"))
            if students_count > 10:
                start = page * 10 - 10
                end = start + 10
                current_page = page
                students = students[start:end]
            else:
                current_page = 1
            print(current_page)

        context = {
            "current_page": current_page,
            "pages_loop": [x for x in range(pages_count)],
            "user": request.user.username,
            "is_teacher": True,
            "students_count": students_count,
            "students": students,
        }

        return render(request, "plattform/student/students.html", context)


class CreateTeacherView(LoginRequiredMixin, View):
    @must_be_teacher
    def get(self, request):
        context = {"teacher": True}
        # use the same html as for students
        return render(request, "plattform/student/create_student.html", context)

    @must_be_teacher
    def post(self, request):
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        context = {"teacher": True}
        if password1 != password2:
            context["error"] = "Passwords didn't match! Try again please."
            return render(request, "plattform/student/create_student.html", context)
        else:
            try:
                if not username or not first_name or not last_name:
                    context["error"] = "Not all data  was provided!"
                    return render(
                        request, "plattform/student/create_student.html", context
                    )
                user_exists = User.objects.get(username=username)
                if user_exists:
                    context["error"] = "User exists!"
                    return render(
                        request, "plattform/student/create_student.html", context
                    )
            except User.DoesNotExist:
                user = User.objects.create_user(username, password=password1)
                user.save()
                user_info = Profile(
                    user=user,
                    is_teacher=True,
                    first_name=first_name,
                    last_name=last_name,
                )
                user_info.save()
                context["user"] = user

                return redirect(reverse("plattform:other_profile", args=(user.id,)))


class DeleteTeacherView(LoginRequiredMixin, View):
    def post(self, request, teacher_id):
        if not request.user.is_staff:
            return HttpResponse("Forbidden!")

        teacher = get_object_or_404(User, pk=teacher_id)
        teacher.delete()
        return redirect(reverse("plattform:teachers"))


class TeachersView(LoginRequiredMixin, View):
    @must_be_teacher
    def get(self, request):
        context = {"is_teacher": True}
        admin = User.objects.get(is_staff=True)
        teachers = (
            Profile.objects.filter(is_teacher=True).exclude(user=admin).order_by("user")
        )
        is_admin = request.user.is_staff

        PAGE_SPLITTER = 10
        remainder = len(teachers) / PAGE_SPLITTER
        teachers_count = len(teachers)

        if remainder < 1:
            pages_count = 1
        if remainder % 1 != 0:
            pages_count = int(remainder) + 1
        else:
            pages_count = int(remainder)

        if not request.GET.get("page"):
            current_page = 1
            if teachers_count > PAGE_SPLITTER:
                teachers = teachers[:PAGE_SPLITTER]

        else:
            page = int(request.GET.get("page"))
            if teachers_count > PAGE_SPLITTER:
                start = page * PAGE_SPLITTER - PAGE_SPLITTER
                end = start + PAGE_SPLITTER
                current_page = page
                teachers = teachers[start:end]
            else:
                current_page = 1

        context["teachers"] = teachers
        context["is_admin"] = is_admin

        context["current_page"] = current_page
        context["pages_loop"] = [x for x in range(pages_count)]
        context["teachers_count"] = teachers_count

        return render(request, "plattform/teachers.html", context)


class StudentCreateView(LoginRequiredMixin, View):
    @must_be_teacher
    def get(self, request):

        context = {"is_teacher": True}
        return render(request, "plattform/student/create_student.html", context)

    @must_be_teacher
    def post(self, request):
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        context = {"is_teacher": True}
        if password1 != password2:
            context["error"] = "Passwords didn't match! Try again please."
            return render(request, "plattform/student/create_student.html", context)
        else:
            try:
                if not username or not first_name or not last_name:
                    context["error"] = "Not all data  was provided!"
                    return render(
                        request, "plattform/student/create_student.html", context
                    )
                user_exists = User.objects.get(username=username)
                if user_exists:
                    context["error"] = "User exists!"
                    return render(
                        request, "plattform/student/create_student.html", context
                    )
            except User.DoesNotExist:
                user = User.objects.create_user(username, password=password1)
                user.save()
                user_info = Profile(
                    user=user,
                    is_teacher=False,
                    first_name=first_name,
                    last_name=last_name,
                )
                user_info.save()
        return redirect(reverse("plattform:students"))


class ChangePasswordView(LoginRequiredMixin, View):
    @must_be_teacher
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        context = {"user": user, "is_teacher": True}
        return render(request, "plattform/student/change_password.html", context)

    @must_be_teacher
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        password_1 = request.POST.get("password_1")
        password_2 = request.POST.get("password_2")
        context = {"user": user, "is_teacher": True}
        if password_1 != password_2:
            context["error"] = "Passwords didn't match. Please enter again."
        else:
            user.set_password(password_1)
            user.save()
            context["success"] = True
            return render(request, "plattform/student/change_password.html", context)
        return render(request, "plattform/student/change_password.html", context)


class StudentDeleteView(LoginRequiredMixin, View):
    @must_be_teacher
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return redirect(reverse("plattform:students"))


class CourseDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        subscriber = Subscriber.objects.filter(course=pk).filter(user=request.user.id)
        is_teacher = Profile.objects.get(user=request.user.id).is_teacher
        if subscriber or is_teacher:

            course = get_object_or_404(Course, pk=pk)
            course_description = course.description
            if not is_teacher:
                progress = subscriber[0].calculate_progress()

            else:
                progress = 0

            modules = Module.objects.filter(course=pk)

            if subscriber:
                gots_exist = Got.objects.filter(subscriber=subscriber[0])
            else:
                gots_exist = False

            modules_data = []

            for module in modules:
                topics = Topic.objects.filter(module=module.id)

                if subscriber:
                    if topics:
                        if not gots_exist or len(gots_exist) != len(topics):
                            for topic in topics:
                                already_exists = Got.objects.filter(
                                    topic=topic, subscriber=subscriber[0]
                                ).exists()
                                if already_exists:
                                    continue
                                got = Got(topic=topic, subscriber=subscriber[0])
                                got.save()

                quizes = Quiz.objects.filter(module=module)
                if is_teacher:
                    data = {
                        "topics": [
                            {"topic": topic, "got": {"got": False}} for topic in topics
                        ]
                    }
                else:
                    if topics:
                        data = {
                            "topics": [
                                {
                                    "topic": topic,
                                    "got": Got.objects.get_or_create(
                                        subscriber=subscriber[0], topic=topic
                                    )[0],
                                }
                                for topic in topics
                            ]
                        }
                    else:
                        data = {
                            "topics": [
                                {"topic": topic, "got": False} for topic in topics
                            ]
                        }

                if len(quizes) == 0:

                    modules_data.append(
                        {"module_name": module.name, "topics": data, "module": module}
                    )
                else:
                    quiz_data = []

                    for quiz in quizes:
                        if is_teacher:
                            quiz_data.append(
                                {"quiz": quiz, "quiz_result": {"result": 0}}
                            )
                            continue
                        quiz_result, created = QuizResult.objects.get_or_create(
                            quiz=quiz,
                            module=module,
                            subscriber=subscriber[0],
                            course=course,
                        )

                        quiz_data.append({"quiz": quiz, "quiz_result": quiz_result})
                    modules_data.append(
                        {
                            "module_name": module.name,
                            "topics": data,
                            "module": module,
                            "quizes": quiz_data,
                        }
                    )

            context = {
                "course": course,
                "progress": progress,
                "course_description": course_description,
                "modules_data": modules_data,
                "is_teacher": is_teacher,
            }

            return render(request, "plattform/course_detail.html", context)
        else:
            return HttpResponse(
                "You are not subscribed to this course or this course is unavaliable,please contact a manager"
            )


class TopicDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        is_teacher = Profile.objects.get(user=request.user.id).is_teacher

        topic = get_object_or_404(Topic, pk=pk)
        course_id = topic.module.course.id
        is_subscribed = Subscriber.objects.filter(course=course_id).filter(
            user=request.user.id
        )
        if is_subscribed or is_teacher:

            if is_subscribed:
                obj, created = Got.objects.get_or_create(
                    subscriber=is_subscribed[0], topic=topic
                )
                context = {"topic": topic, "is_teacher": is_teacher, "got": obj.got}

            else:
                context = {"topic": topic, "is_teacher": is_teacher}

            return render(request, "plattform/topic_detail.html", context)
        else:
            return HttpResponse(
                "You are not subscribed to this topic,please contact a manager"
            )

    def post(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        course_id = topic.module.course.id
        is_subscribed = Subscriber.objects.filter(course=course_id).filter(
            user=request.user.id
        )
        if is_subscribed:
            data = dict(json.loads(request.body))
            got, created = Got.objects.get_or_create(subscriber=is_subscribed[0], topic=topic)
            if data["state"] == "checked":
                got.got = True
            else:
                got.got = False
            got.save()
            return JsonResponse({"ok": "ok"})
        else:
            return HttpResponse("Forbidden!")


class CoursesView(LoginRequiredMixin, View):
    @must_be_teacher
    def get(self, request):
        context = {"is_teacher": True}
        courses = Course.objects.all()

        PAGE_SPLITTER = 5
        remainder = len(courses) / PAGE_SPLITTER
        courses_count = len(courses)

        if remainder < 1:
            pages_count = 1
        if remainder % 1 != 0:
            pages_count = int(remainder) + 1
        else:
            pages_count = int(remainder)

        if not request.GET.get("page"):
            current_page = 1
            if courses_count > PAGE_SPLITTER:
                courses = courses[:PAGE_SPLITTER]

        else:
            page = int(request.GET.get("page"))
            if courses_count > PAGE_SPLITTER:
                start = page * PAGE_SPLITTER - PAGE_SPLITTER
                end = start + PAGE_SPLITTER
                current_page = page
                courses = courses[start:end]
            else:
                current_page = 1

        courses = [
            {"is_author": course.author == request.user, "course": course}
            for course in courses
        ]

        context["courses"] = courses
        context["current_page"] = current_page
        context["pages_loop"] = [x for x in range(pages_count)]
        context["courses_count"] = courses_count
        return render(request, "plattform/course/courses.html", context)


class GradebookView(LoginRequiredMixin, View):
    @must_be_teacher
    def get(self, request, course_id):
        subscribers = Subscriber.objects.filter(course=course_id).order_by("user")
        course_name = get_object_or_404(Course, pk=course_id)
        users_data = []

        for subscriber in subscribers:
            user = subscriber.user
            first_name = user.profile.first_name
            last_name = user.profile.last_name
            full_name = first_name + " " + last_name
            progress = subscriber.calculate_progress()
            users_data.append({"name": full_name, "progress": progress, "user": user})
        context = {"students_table": users_data, "course_name": course_name}

        return render(request, "plattform/course/gradebook.html", context)

    @must_be_teacher
    def post(self, request, course_id):
        subscribers = Subscriber.objects.filter(course=course_id).order_by("user")
        students = []
        results = []
        for subscriber in subscribers:
            user = subscriber.user
            first_name = user.profile.first_name
            last_name = user.profile.last_name
            full_name = first_name + " " + last_name
            progress = subscriber.calculate_progress()
            students.append(full_name)
            results.append(progress)

        context = {
            "students_names": students,
            "students_results": results,
        }
        return JsonResponse(context)


class CourseCreateView(LoginRequiredMixin, View):
    @must_be_teacher
    def get(self, request):
        form = CourseForm()
        context = {"is_teacher": True, "form": form}
        return render(request, "plattform/course/add_course.html", context)

    @must_be_teacher
    def post(self, request):
        form = CourseForm(request.POST, request.FILES)

        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user
            course.save()
            course_id = course.id
            return redirect(reverse("plattform:edit_course", args=(course_id,)))
        else:
            return HttpResponse("Error")


class CourseEditView(LoginRequiredMixin, View):
    @must_be_author(related_to="course", action="edit")
    @must_be_teacher
    def get(self, request, pk):
        course = Course.objects.get(id=pk)
        modules = Module.objects.filter(course=pk)

        modules_data = []

        for module in modules:
            topics = Topic.objects.filter(module=module.id)
            quizes = Quiz.objects.filter(module=module)
            if len(quizes) == 0:
                modules_data.append(
                    {"module_name": module.name, "topics": topics, "id": module.id}
                )
            else:
                modules_data.append(
                    {
                        "module_name": module.name,
                        "topics": topics,
                        "id": module.id,
                        "quizes": quizes,
                    }
                )

        context = {"course": course, "modules_data": modules_data}
        context["is_teacher"] = True
        context["form"] = CourseForm(instance=course)
        context["course_id"] = pk
        return render(request, "plattform/course/course_edit.html", context)

    @must_be_author(related_to="course", action="edit")
    @must_be_teacher
    def post(self, request, pk):
        course = Course.objects.get(id=pk)
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect(reverse("plattform:edit_course", args=(pk,)))
        else:
            HttpResponse("error")


class CourseDeleteView(LoginRequiredMixin, View):
    @must_be_author(related_to="course", action="delete")
    @must_be_teacher
    def post(self, request, pk):
        course = Course.objects.get(id=pk)
        course.delete()
        return redirect("plattform:courses")


class CourseSubscribersView(LoginRequiredMixin, View):
    @must_be_allowed_to_modify_subscriber(action="delete")
    @must_be_teacher
    def get(self, request, pk):
        course = Course.objects.get(pk=pk)
        subscribers = Subscriber.objects.filter(course=pk).order_by("user")

        PAGE_SPLITTER = 10
        remainder = len(subscribers) / PAGE_SPLITTER
        subscribers_count = len(subscribers)

        if remainder < 1:
            pages_count = 1
        if remainder % 1 != 0:
            pages_count = int(remainder) + 1
        else:
            pages_count = int(remainder)

        if not request.GET.get("page"):
            current_page = 1
            if subscribers_count > PAGE_SPLITTER:
                subscribers = subscribers[:PAGE_SPLITTER]

        else:
            page = int(request.GET.get("page"))
            if subscribers_count > PAGE_SPLITTER:
                start = page * PAGE_SPLITTER - PAGE_SPLITTER
                end = start + PAGE_SPLITTER
                current_page = page
                subscribers = subscribers[start:end]
            else:
                current_page = 1

        context = {
            "is_teacher": True,
            "current_page": current_page,
            "pages_loop": [x for x in range(pages_count)],
            "subscribers_count": subscribers_count,
            "subscribers": subscribers,
            "course": course,
        }
        return render(request, "plattform/course/course_subscribers.html", context)


class SubscriberDeleteView(LoginRequiredMixin, View):
    @must_be_allowed_to_modify_subscriber(action="delete")
    @must_be_teacher
    def post(self, request):
        user_id = request.GET.get("user")
        course_id = request.GET.get("course")
        record = Subscriber.objects.filter(user=user_id).filter(course=course_id)
        record.delete()
        return HttpResponse("ok")


class SubscriberAddView(LoginRequiredMixin, View):
    @must_be_allowed_to_modify_subscriber(action="add")
    @must_be_teacher
    def get(self, request, pk):

        course = Course.objects.get(pk=pk)
        users = User.objects.all().order_by("id")

        not_subscribed = []

        for user in users:

            user_is_teacher = Profile.objects.get(user=user)

            if user_is_teacher.is_teacher:
                continue

            exists_in_course_table = Subscriber.objects.filter(user=user)

            if not exists_in_course_table:
                not_subscribed.append(user)
                continue

            exists_in_this_course = Subscriber.objects.filter(user=user).filter(
                course=pk
            )
            exists_in_other = Subscriber.objects.filter(user=user).exclude(
                course=course
            )
            if (exists_in_this_course and exists_in_other) or exists_in_this_course:
                continue

            else:
                not_subscribed.append(user)

        PAGE_SPLITTER = 10
        remainder = len(not_subscribed) / PAGE_SPLITTER
        not_subscribers_count = len(not_subscribed)

        if remainder < 1:
            pages_count = 1
        if remainder % 1 != 0:
            pages_count = int(remainder) + 1
        else:
            pages_count = int(remainder)

        if not request.GET.get("page"):
            current_page = 1
            if not_subscribers_count > PAGE_SPLITTER:
                not_subscribed = not_subscribed[:PAGE_SPLITTER]

        else:
            page = int(request.GET.get("page"))
            if not_subscribers_count > PAGE_SPLITTER:
                start = page * PAGE_SPLITTER - PAGE_SPLITTER
                end = start + PAGE_SPLITTER
                current_page = page
                not_subscribed = not_subscribed[start:end]
            else:
                current_page = 1

        context = {
            "is_teacher": True,
            "current_page": current_page,
            "pages_loop": [x for x in range(pages_count)],
            "not_subscribers_count": not_subscribers_count,
            "users": not_subscribed,
            "course": course,
        }
        return render(request, "plattform/course/not_subscribed.html", context)

    @must_be_allowed_to_modify_subscriber(action="add")
    @must_be_teacher
    def post(self, request, pk):
        user_id = request.POST.get("user")

        user = User.objects.get(pk=user_id)
        course = Course.objects.get(pk=pk)
        subscriber = Subscriber(user=user, course=course)
        subscriber.save()
        modules = Module.objects.filter(course=course)

        for module in modules:
            topics = Topic.objects.filter(module=module.id)

            # add "Got objects" and "QuizResult objects" for a student,for optimization purposes

            if topics:

                for topic in topics:
                    got = Got(topic=topic, subscriber=subscriber)
                    got.save()
            quizes = Quiz.objects.filter(course=course, module=module)

            for quiz in quizes:
                quiz_result = QuizResult(
                    course=course, module=module, subscriber=subscriber, quiz=quiz
                )
                quiz_result.save()

        return redirect(reverse("plattform:course_subscribers", args=(pk,)))


class ModuleAddView(LoginRequiredMixin, View):
    @must_be_teacher
    def get(self, request):

        courses = Course.objects.filter(author=request.user)
        context = {"courses": courses}
        return render(request, "plattform/module/add_module.html", context)

    @must_be_author(related_to="module", action="add")
    @must_be_teacher
    def post(self, request):
        form = ModuleForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(
                reverse("plattform:edit_course", args=(request.POST.get("course"),))
            )
        else:
            return HttpResponse("error")


class ModuleEditView(LoginRequiredMixin, View):
    @must_be_author(related_to="module", action="edit")
    @must_be_teacher
    def get(self, request, pk):
        module = Module.objects.get(pk=pk)
        form = ModuleForm(instance=module)
        courses = Course.objects.filter(author=request.user).exclude(
            name=module.course.name
        )
        context = {"form": form, "courses": courses, "module": module}
        return render(request, "plattform/module/module_edit.html", context)

    @must_be_author(related_to="module", action="edit")
    @must_be_teacher
    def post(self, request, pk):
        module = Module.objects.get(pk=pk)
        form = ModuleForm(request.POST, instance=module)

        if form.is_valid():
            form.save()
            return redirect(
                reverse("plattform:edit_course", args=(request.POST.get("course"),))
            )
        else:
            return HttpResponse("error")


class ModuleDeleteView(LoginRequiredMixin, View):
    @must_be_author(related_to="module", action="delete")
    @must_be_teacher
    def post(self, request, pk):
        module = Module.objects.get(pk=pk)
        module.delete()
        return HttpResponse("ok")


class TopicAddView(LoginRequiredMixin, View):
    @must_be_teacher
    def get(self, request):
        form = TopicForm()
        courses = Course.objects.filter(author=request.user)
        modules = Module.objects.filter(course_id__in=courses)
        context = {"form": form, "modules": modules}
        return render(request, "plattform/topic/add_topic.html", context)

    @must_be_author(related_to="topic", action="add")
    @must_be_teacher
    def post(self, request):
        form = TopicForm(request.POST)

        if form.is_valid():
            topic = form.save(commit=False)

            topic.name = request.POST.get("name")
            topic.module = Module.objects.get(pk=request.POST.get("module"))

            topic.save()
            course_id = topic.module.course.id
            return redirect(reverse("plattform:edit_course", args=(course_id,)))
        else:
            return HttpResponse("Error")


class TopicEditView(LoginRequiredMixin, View):
    @must_be_author(related_to="topic", action="edit")
    @must_be_teacher
    def get(self, request, pk):
        topic = Topic.objects.get(pk=pk)
        teacher = User.objects.get(pk=request.user.id)
        courses = Course.objects.filter(author=teacher)
        course = topic.module.course
        modules = Module.objects.filter(course_id__in=courses).exclude(
            pk=topic.module.id
        )

        form = TopicForm(instance=topic)
        context = {"course": course, "form": form, "topic": topic, "modules": modules}
        return render(request, "plattform/topic/edit_topic.html", context)

    @must_be_author(related_to="topic", action="edit")
    @must_be_teacher
    def post(self, request, pk):
        topic = Topic.objects.get(pk=pk)
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            topic.name = request.POST.get("name")
            topic.image = request.POST.get("image")

            topic.module = Module.objects.get(pk=request.POST.get("module"))

            topic.save()

            course_id = topic.module.course.id
            form.save()
            return redirect(reverse("plattform:edit_course", args=(course_id,)))
        else:
            text = (
                "The topic content didn't pass our security validators."
                "The topic content looks like cross-site-scripting attack (XSS), check the content again."
                "Maybe you added some tags/attributes that trigger javascript to execute."
            )
            return HttpResponse(text)


class TopicDeleteView(LoginRequiredMixin, View):
    @must_be_author(related_to="topic", action="delete")
    @must_be_teacher
    def post(self, request, pk):
        topic = Topic.objects.get(pk=pk)
        course_id = topic.module.course.id
        topic.delete()
        return redirect(reverse("plattform:edit_course", args=(course_id,)))


class PersonalProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        profile = user.profile
        is_teacher = Profile.objects.get(user=request.user.id).is_teacher
        context = {"user": user, "profile": profile, "is_teacher": is_teacher}
        return render(request, "plattform/profile/profile.html", context)


class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        user = Profile.objects.get(user=request.user)
        is_teacher = Profile.objects.get(user=request.user.id).is_teacher
        context = {
            "about": user.about,
            "image": user.image,
            "is_teacher": is_teacher,
        }

        return render(request, "plattform/profile/profile_edit.html", context)

    def post(self, request):
        instance = Profile.objects.get(user=request.user)
        form = ProfileForm(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            form.save()
            return redirect(reverse("plattform:profile"))
        else:
            return HttpResponse("Oops...some error :(")


class ChangeSelfPasswordView(LoginRequiredMixin, View):
    def get(self, request):
        is_teacher = Profile.objects.get(user=request.user.id).is_teacher
        context = {"is_teacher": is_teacher}
        return render(request, "plattform/profile/change_self_password.html", context)

    def post(self, request):
        is_teacher = Profile.objects.get(user=request.user.id).is_teacher
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        new_password2 = request.POST.get("new_password2")
        user = User.objects.get(pk=request.user.id)

        pass_is_correct = user.check_password(current_password)
        context = {"is_teacher": is_teacher}
        if pass_is_correct:
            if new_password != new_password2:
                context["error"] = "New passwords didn't match. Please enter again."
            else:
                user.set_password(new_password)
                user.save()
                context["success"] = True
                return render(
                    request, "plattform/profile/change_self_password.html", context
                )

        else:
            context["error"] = "Wrong current password!"
        return render(request, "plattform/profile/change_self_password.html", context)


class OtherProfileView(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        profile = user.profile

        # redirect if other profile is user's profile
        if request.user.id == pk:
            return redirect(reverse("plattform:profile"))
        is_teacher = Profile.objects.get(user=request.user.id).is_teacher
        teacher_profile = Profile.objects.get(user=pk).is_teacher

        if is_teacher:
            subscriptions = Subscriber.objects.filter(user=user)
            courses_data = []
            for subs in subscriptions:
                course = subs.course
                modules = Module.objects.filter(course=subs.course)
                topic_amount = 0
                completed_topics = 0
                quizes_amount = 0
                quizes_passed = 0
                quizes_passed_objects = []
                quizes_between_50_100 = 0
                quizes_between_50_100_objects = []
                quizes_lte_50 = 0
                quizes_lte_50_objects = []
                quiz_points = 0
                completed_topics_names = []
                for module in modules:
                    topics = Topic.objects.filter(module=module)
                    quizes = Quiz.objects.filter(module=module)
                    quizes_amount += len(quizes)

                    for quiz in quizes:
                        quiz_result, created = QuizResult.objects.get_or_create(
                            quiz=quiz,
                            module=module,
                            course=subs.course,
                            subscriber=subs,
                        )
                        quiz_points += quiz_result.result
                        if quiz_result.result == 100:
                            quizes_passed += 1
                            quizes_passed_objects.append(
                                {"result": quiz_result, "quiz": quiz_result.quiz}
                            )
                        if quiz_result.result <= 50 and quiz_result.result != 0:
                            quizes_lte_50 += 1
                            quizes_lte_50_objects.append(
                                {"result": quiz_result, "quiz": quiz_result.quiz}
                            )
                        if 50 < quiz_result.result < 100:
                            quizes_between_50_100 += 1

                            quizes_between_50_100_objects.append(
                                {"result": quiz_result, "quiz": quiz_result.quiz}
                            )

                    for topic in topics:
                        topic_amount += 1
                        got, created = Got.objects.get_or_create(
                            topic=topic, subscriber=subs
                        )
                        if got.got:
                            completed_topics += 1
                            completed_topics_names.append(topic)

                user_progress_points = completed_topics + quiz_points
                total_progress_points = quizes_amount * 100 + topic_amount
                topics_completed = str(completed_topics) + "/" + str(topic_amount)
                try:
                    progress = (user_progress_points * 100) / total_progress_points
                except ZeroDivisionError:
                    progress = 0

                passed_quizes = str(quizes_passed) + "/" + str(quizes_amount)
                between_50_100_quizes = (
                        str(quizes_between_50_100) + "/" + str(quizes_amount)
                )
                lte_50_quizes = str(quizes_lte_50) + "/" + str(quizes_amount)
                courses_data.append(
                    {
                        "course": course,
                        "topics_completed": {
                            "amount": topics_completed,
                            "names": completed_topics_names,
                        },
                        "quizes_passed": {
                            "amount": passed_quizes,
                            "names": quizes_passed_objects,
                        },
                        "quizes_between_50_100": {
                            "amount": between_50_100_quizes,
                            "names": quizes_between_50_100_objects,
                        },
                        "quizes_lte_50": {
                            "amount": lte_50_quizes,
                            "names": quizes_lte_50_objects,
                        },
                        "progress": round(progress),
                    }
                )

            context = {
                "teacher_profile": teacher_profile,
                "user": user,
                "profile": profile,
                "is_teacher": is_teacher,
                "courses_data": courses_data,
            }

        else:
            context = {"user": user, "profile": profile, "is_teacher": is_teacher}
        return render(request, "plattform/profile/profile_other.html", context)


class ClassmatesView(LoginRequiredMixin, View):
    def get(self, request, pk):
        is_subscribed = Subscriber.objects.filter(user=request.user).filter(course=pk)

        if is_subscribed:
            classmates = Subscriber.objects.filter(course=pk).exclude(user=request.user)
            course = Course.objects.get(pk=pk)
            context = {"classmates": classmates, "course": course}
            return render(request, "plattform/classmates.html", context)
        else:
            return HttpResponse(
                "There is no such course or you are not authorized to see a content of this page.Please contact a manager."
            )


class QuizView(LoginRequiredMixin, View):
    def get(self, request, module_id, quiz_id):

        course = get_object_or_404(Module, pk=module_id).course
        is_subscribed = Subscriber.objects.filter(course=course).filter(
            user=request.user.id
        )
        is_teacher = Profile.objects.get(user=request.user.id).is_teacher
        is_wrong_combination = Quiz.objects.filter(module=module_id).filter(pk=quiz_id)

        if len(is_wrong_combination) == 0:
            return HttpResponse("You are not authorized to pass this quiz!")
        if is_subscribed or is_teacher:

            quiz = Quiz.objects.get(pk=quiz_id)
            questions = Question.objects.filter(quiz=quiz)
            data = []
            questions_number = len(questions)

            for question in questions:
                ans = question.answers.all()
                ans_limit = len(
                    Answer.objects.filter(is_correct=True, question=question)
                )
                data.append(
                    {"question": question, "ans_limit": ans_limit, "answers": ans}
                )

            for q in data:
                q["answers"] = list(q["answers"])
                random.shuffle(q["answers"])

            random.shuffle(data)
            context = {
                "data": data,
                "module_id": module_id,
                "quiz_id": quiz_id,
                "quiz_name": quiz.name,
                "is_teacher": is_teacher,
                "questions_number": {
                    "number": questions_number,
                    "list": [x for x in range(1, questions_number + 1)],
                },
            }

            return render(request, "plattform/quiz.html", context)
        else:
            return HttpResponse("You are not authorized to pass this quiz!")


class CheckResultsView(LoginRequiredMixin, View):
    def post(self, request):
        data = dict(json.loads(request.body))
        if not data["answers"]:
            return JsonResponse({"error": "No data was provided!"})
        module_id = data["module_id"]
        module = get_object_or_404(Module, pk=module_id)
        quiz_id = data["quiz_id"]
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        course = get_object_or_404(Module, pk=module_id).course
        is_subscribed = Subscriber.objects.filter(course=course).filter(
            user=request.user.id
        )
        is_teacher = Profile.objects.get(user=request.user.id).is_teacher
        is_wrong_combination = Quiz.objects.filter(module=module_id).filter(pk=quiz_id)

        if len(is_wrong_combination) == 0:
            return HttpResponse("Error")
        if is_subscribed or is_teacher:
            total_score = 0
            score = 0
            user_answers_data = data["answers"]
            questions = Question.objects.filter(quiz=quiz_id)

            wrong_answers = {}
            for question in questions:
                correct_answers = [
                    str(ans.name) for ans in question.answers.filter(is_correct=True)
                ]
                total_score += len(correct_answers)
                user_answers = user_answers_data.get(str(question.name))

                # check if there are not any answers for a question
                if not user_answers:
                    continue

                # check if too many answers were provided,because without this condition
                # a user can send all options for a question and get max result.
                if len(correct_answers) < len(user_answers):
                    return JsonResponse({"error": "Too many answers were provided"})

                for user_answer in user_answers:

                    if user_answer in correct_answers:
                        score += 1
                    else:
                        if wrong_answers.get(question.name):
                            wrong_answers[question.name].append(user_answer)
                        else:
                            wrong_answers[question.name] = []
                            wrong_answers[question.name].append(user_answer)

            result = int((score * 100) / total_score)

            # do not create quiz results for teachers
            if is_subscribed:
                quiz_result, created = QuizResult.objects.get_or_create(
                    quiz=quiz, module=module, course=course, subscriber=is_subscribed[0]
                )

                quiz_result.result = result
                quiz_result.save()
            score = f"{score}/{total_score}"

            return JsonResponse({"score": score, "wrong_answers": wrong_answers})
        else:
            return JsonResponse({"error": "access denied"})


class CreateQuizView(LoginRequiredMixin, View):
    @must_be_author(related_to="quiz", action="add")
    @must_be_teacher
    def get(self, request):
        module = Module.objects.get(pk=request.GET.get("module_id"))
        context = {"is_teacher": True, "module": module}
        return render(request, "plattform/quiz/create_quiz.html", context)

    @must_be_author(related_to="quiz", action="add")
    @must_be_teacher
    def post(self, request):

        data = dict(json.loads(request.body))
        module = Module.objects.get(id=data["module_id"])
        course = module.course

        # Data validation
        if Quiz.objects.filter(name=data["quiz_name"]).filter(course=course).exists():
            return JsonResponse({"error": "Quiz name exists!"})
        elif not data["quiz_name"] or not data["questions"]:
            return JsonResponse({"error": "No quiz name or question\s"})

        else:

            quiz = Quiz(name=data["quiz_name"].strip(), course=course, module=module)
            questions = data["questions"]
            q_names = []
            for question in questions:
                if not question["question_text"]:
                    return JsonResponse({"error": "Empty question\s field!"})
                answers = question["answers"]
                if not answers:
                    return JsonResponse({"error": "No answers for question\s"})
                a_names = []
                a_ans = []
                for answer in answers:
                    a_names.append(answer["answer_text"])
                    a_ans.append(answer["is_correct"])
                if len(set(a_names)) != len(a_names):
                    return JsonResponse({"error": "Repetitive answer\s in question\s"})
                elif "" in a_names:
                    return JsonResponse({"error": "Empty answer!"})
                if not True in a_ans:
                    return JsonResponse(
                        {"error": "No correct answer in some question\s!"}
                    )
                q_names.append(question["question_text"])
            if len(set(q_names)) != len(q_names):
                return JsonResponse({"error": "Repetitive question/s!"})

            # Save quiz to db
            quiz.save()
            for question in questions:
                question_obj = Question(name=question["question_text"], quiz=quiz)
                question_obj.save()
                answers = question["answers"]
                for answer in answers:
                    answer_obj = Answer(
                        question=question_obj,
                        name=answer["answer_text"],
                        is_correct=answer["is_correct"],
                    )
                    answer_obj.save()
        redirect_url = reverse("plattform:quiz", args=(module.id, quiz.id))
        return JsonResponse({"success": True, "redirect_to": redirect_url})


class EditQuizView(LoginRequiredMixin, View):
    @must_be_author(related_to="quiz", action="edit")
    @must_be_teacher
    def get(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        course = quiz.course
        questions = []
        ans_counter = 1
        id = 1
        for question in Question.objects.filter(quiz=quiz):
            data = {"question_text": question.name}
            answers = []
            for answer in Answer.objects.filter(question=question):
                ans_data = {
                    "answer_text": answer.name,
                    "is_correct": answer.is_correct,
                    "id": id,
                }
                id += 1
                answers.append(ans_data)
            ans_counter += len(answers)
            data["answers"] = answers
            questions.append(data)
        question_counter = len(questions)

        context = {
            "course": course,
            "quiz": quiz,
            "questions": questions,
            "counter": question_counter + 1,
            "ans_counter": ans_counter,
        }
        return render(request, "plattform/quiz/edit_quiz.html", context)

    @must_be_author(related_to="quiz", action="edit")
    @must_be_teacher
    def post(self, request, quiz_id):
        data = dict(json.loads(request.body))
        quiz_def = Quiz.objects.get(pk=quiz_id)
        course = quiz_def.course
        module = quiz_def.module
        quiz_id = quiz_def.id
        quiz_name = quiz_def.name

        # Data validation
        if (
                Quiz.objects.filter(name=data["quiz_name"])
                        .filter(course=course)
                        .exclude(name=quiz_name)
                        .exists()
        ):
            return JsonResponse({"error": "Quiz name exists!"})
        elif not data["quiz_name"] or not data["questions"]:
            return JsonResponse({"error": "No quiz name or question\s"})

        else:

            questions = data["questions"]
            q_names = []
            for question in questions:
                if not question["question_text"]:
                    return JsonResponse({"error": "Empty question\s field!"})
                answers = question["answers"]
                if not answers:
                    return JsonResponse({"error": "No answers for question\s"})
                a_names = []
                a_ans = []
                for answer in answers:
                    a_names.append(answer["answer_text"])
                    a_ans.append(answer["is_correct"])
                if len(set(a_names)) != len(a_names):
                    return JsonResponse({"error": "Repetitive answer\s in question\s"})
                if not True in a_ans:
                    return JsonResponse(
                        {"error": "No correct answer in some question\s!"}
                    )
                q_names.append(question["question_text"])
            if len(set(q_names)) != len(q_names):
                return JsonResponse({"error": "Repetitive question/s!"})

            quiz_def.delete()
            quiz = Quiz(name=data["quiz_name"], course=course, module=module)
            quiz.id = quiz_id

            # Save quiz to db
            quiz.save()
            for question in questions:
                question_obj = Question(name=question["question_text"], quiz=quiz)
                question_obj.save()
                answers = question["answers"]
                for answer in answers:
                    answer_obj = Answer(
                        question=question_obj,
                        name=answer["answer_text"],
                        is_correct=answer["is_correct"],
                    )
                    answer_obj.save()
        redirect_url = reverse("plattform:quiz", args=(module.id, quiz.id))
        return JsonResponse({"success": True, "redirect_to": redirect_url})


class DeleteQuizView(LoginRequiredMixin, View):
    @must_be_author(related_to="quiz", action="delete")
    @must_be_teacher
    def post(self, request, quiz_id):
        quiz = Quiz.objects.get(pk=quiz_id)
        course = quiz.course
        quiz.delete()
        return redirect(reverse("plattform:edit_course", args=(course.id,)))
