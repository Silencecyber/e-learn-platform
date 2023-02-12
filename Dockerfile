FROM python:3.9-slim-buster
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONNUNBUFFERED 1
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN echo "from django.contrib.auth.models import Users;from plattform.models import Profile;user=User.objects.create_superuser('admin','admin@ad.com','admin');Profile(user=user,is_teacher=True,first_name='admin',last_name='admin').save()" | python manage.py shell
CMD python manage.py runserver 0.0.0.0:8000
