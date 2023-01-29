from django.contrib.auth.models import User
from plattform.models import Profile
from faker import Faker
from faker.providers import lorem

def create_user(fake):

    first_name=fake.first_name()
    user={
        'username':first_name.lower(),
        'password':'1',
        'first_name':first_name,
        'last_name':fake.last_name(),
        'about':fake.sentence(nb_words=10)
    }
    return user


fake=Faker()
student_number=0
teacher_number=10

fake.add_provider(lorem)
print('Started...')
for _ in range(student_number):

    user=create_user(fake)

    try:
        user_exists = User.objects.get(username=user['username'])
        if user_exists:
            print('this username is existed')
            continue
    except User.DoesNotExist:
        new_user = User.objects.create_user(user['username'], password=user['password'])
        new_user.save()
        user_info = Profile(user=new_user,
                             is_teacher=False,
                             first_name=user['first_name'],
                             last_name=user['last_name'],
                             about=user['about'])
        user_info.save()
for _ in range(teacher_number):

    user=create_user(fake)

    try:
        user_exists = User.objects.get(username=user['username'])
        if user_exists:
            print('this username is existed')
            continue
    except User.DoesNotExist:
        new_user = User.objects.create_user(user['username'], password=user['password'])
        new_user.save()
        user_info = Profile(user=new_user,
                             is_teacher=True,
                             first_name=user['first_name'],
                             last_name=user['last_name'],
                             about=user['about'])
        user_info.save()
print('End')