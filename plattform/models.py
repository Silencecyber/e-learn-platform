from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_teacher = models.BooleanField(default=False)
    image = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    about = models.TextField(max_length=500, null=True, blank=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=600)
    image = models.ImageField(upload_to='course_images', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name + " | " + self.course.name


class Topic(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=200)
    image = models.CharField(max_length=500, blank=True, null=True)
    # content=models.TextField()
    content = RichTextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} | Module - {self.module.name} | Course - {self.module.course.name}"


class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscribers')

    def calculate_progress(self):
        total_points = 0
        user_points = 0

        modules = Module.objects.filter(course=self.course)

        for module in modules:
            topics = Topic.objects.filter(module=module)
            total_points += len(topics)
            quizes = Quiz.objects.filter(module=module)
            total_points += len(quizes) * 100

            for quiz in quizes:
                quiz_result, created = QuizResult.objects.get_or_create(quiz=quiz, subscriber=self, module=module,
                                                                        course=quiz.course)
                user_points += quiz_result.result

            for topic in topics:
                got, created = Got.objects.get_or_create(subscriber=self, topic=topic)
                if got.got:
                    user_points += 1

        try:
            final_result = round((user_points * 100) / total_points)
        except ZeroDivisionError:
            final_result = 0

        return final_result

    def __str__(self):
        return self.user.username + " - " + self.course.name


class Quiz(models.Model):
    class Meta:
        verbose_name_plural = "quizes"

    name = models.CharField(max_length=200)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quiz')
    course = models.ForeignKey(Course, on_delete=models.CASCADE,related_name='quizes')

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE,related_name="questions")
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name + " | Quiz - " + self.quiz.name


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    name = models.CharField(max_length=200)
    is_correct = models.BooleanField()

    def __str__(self):
        return self.name + " | QUESTION - " + self.question.name


class Got(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    got = models.BooleanField(default=False)

    def __str__(self):
        return self.subscriber.user.username + " - " + self.topic.name + " | Got: " + str(self.got)


class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    result = models.IntegerField(default=0, null=True)

    def __str__(self):
        return "Quiz: " + self.quiz.name + "| Username: " + self.subscriber.user.username + " | Result:  " + str(
            self.result) + " | Module: " + self.module.name + " | Course: " + self.course.name
