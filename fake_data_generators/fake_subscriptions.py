from plattform.models import Subscriber,Course
from django.contrib.auth.models import User
import random

courses=Course.objects.all()
students=[ user  for user in User.objects.all() if not  user.profile.is_teacher ]

for _ in range(len(students)):
    course=random.choice(courses)
    student=random.choice(students)
    if Subscriber.objects.filter(user=student,course=course).exists():
        continue
    else:
        subscriber=Subscriber(user=student,course=course)
        subscriber.save()


