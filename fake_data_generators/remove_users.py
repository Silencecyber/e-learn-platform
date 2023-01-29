from django.contrib.auth.models import User
from plattform.models import Profile


students=Profile.objects.filter(is_teacher=False)
admin=User.objects.get(is_staff=True)
teachers=Profile.objects.filter(is_teacher=True).exclude(user=admin)
for student in students:

    user=student.user

    user.delete()

for teacher in teachers:

    user=teacher.user

    user.delete()







