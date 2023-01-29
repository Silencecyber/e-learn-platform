from faker import Faker
from django.contrib.auth.models import User
from faker.providers import lorem
from plattform.models import Course,Module,Topic,Quiz,Question,Answer,Profile
import random


def create_course(fake):
    course = {
        'name': fake.sentence(nb_words=4),
        'description': fake.paragraph(nb_sentences=3),
        'img': 'no'
    }

    return course

def create_module(fake,course):

    module={
        'course':course,
        'name':fake.sentence(nb_words=4)
    }
    return module

def create_topic(fake,module):

    content="""
    <h4>Introduction</h4>

<p>Mi tincidunt elit, id quisque ligula ac diam, amet. Vel etiam suspendisse morbi eleifend faucibus eget vestibulum felis. Dictum quis montes, sit sit. Tellus aliquam enim urna, etiam. Mauris posuere vulputate arcu amet, vitae nisi, tellus tincidunt. At feugiat sapien varius id.</p>

<p>Eget quis mi enim, leo lacinia pharetra, semper. Eget in volutpat mollis at volutpat lectus velit, sed auctor. Porttitor fames arcu quis fusce augue enim. Quis at habitant diam at. Suscipit tristique risus, at donec. In turpis vel et quam imperdiet. Ipsum molestie aliquet sodales id est ac volutpat.</p>

<div><img alt="Man working at desk" src="https://random.imagecdn.app/750/300" />
<p>Image caption goes here</p>

<h6>Dolor enim eu tortor urna sed duis nulla. Aliquam vestibulum, nulla odio nisl vitae. In aliquet pellentesque aenean hac vestibulum turpis mi bibendum diam. Tempor integer aliquam in vitae malesuada fringilla.</h6>

<p>Elit nisi in eleifend sed nisi. Pulvinar at orci, proin imperdiet commodo consectetur convallis risus. Sed condimentum enim dignissim adipiscing faucibus consequat, urna. Viverra purus et erat auctor aliquam. Risus, volutpat vulputate posuere purus sit congue convallis aliquet. Arcu id augue ut feugiat donec porttitor neque. Mauris, neque ultricies eu vestibulum, bibendum quam lorem id. Dolor lacus, eget nunc lectus in tellus, pharetra, porttitor.</p>

<blockquote>&quot;Ipsum sit mattis nulla quam nulla. Gravida id gravida ac enim mauris id. Non pellentesque congue eget consectetur turpis. Sapien, dictum molestie sem tempor. Diam elit, orci, tincidunt aenean tempus.&quot;</blockquote>

<p>Tristique odio senectus nam posuere ornare leo metus, ultricies. Blandit duis ultricies vulputate morbi feugiat cras placerat elit. Aliquam tellus lorem sed ac. Montes, sed mattis pellentesque suscipit accumsan. Cursus viverra aenean magna risus elementum faucibus molestie pellentesque. Arcu ultricies sed mauris vestibulum.</p>

<h5>Conclusion</h5>

<p>Morbi sed imperdiet in ipsum, adipiscing elit dui lectus. Tellus id scelerisque est ultricies ultricies. Duis est sit sed leo nisl, blandit elit sagittis. Quisque tristique consequat quam sed. Nisl at scelerisque amet nulla purus habitasse.</p>

<p>Nunc sed faucibus bibendum feugiat sed interdum. Ipsum egestas condimentum mi massa. In tincidunt pharetra consectetur sed duis facilisis metus. Etiam egestas in nec sed et. Quis lobortis at sit dictum eget nibh tortor commodo cursus.</p>

<p>Odio felis sagittis, morbi feugiat tortor vitae feugiat fusce aliquet. Nam elementum urna nisi aliquet erat dolor enim. Ornare id morbi eget ipsum. Aliquam senectus neque ut id eget consectetur dictum. Donec posuere pharetra odio consequat scelerisque et, nunc tortor. Nulla adipiscing erat a erat. Condimentum lorem posuere gravida enim posuere cursus diam.</p>
</div>

    """


    topic={
        'name':fake.sentence(nb_words=4),
        'module':module,
        'content':content,
        'image':"https://random.imagecdn.app/500/150"
    }
    return topic

def create_quiz(fake,question_count,answer_count):
    quiz={}
    quiz_name=fake.sentence(nb_words=4)
    questions=[]
    for _ in range(question_count):
        question=fake.sentence(nb_words=7)+"?"
        answers=[]
        for _ in range(answer_count):
            answer=fake.sentence(nb_words=4)
            answers.append({'answer_name':answer,'is_correct':False})
        answers[0]['is_correct']=True
        questions.append({'question_name':question,'answers':answers})
    return {'quiz_name':quiz_name,'questions':questions}


fake = Faker()
fake.add_provider(lorem)

COURSE_NUMBER=2
MODULE_NUMBER=3
TOPIC_NUMBER=4
COUNT_QUESTION=5
COUNT_ANSWERS=3
COUNT_QUIZ=1





print('Started.....')
teachers=Profile.objects.filter(is_teacher=True)

for _ in range(COURSE_NUMBER):

    module_number = MODULE_NUMBER + random.randint(0, 2)
    topic_number = TOPIC_NUMBER + random.randint(0, 3)
    count_question = COUNT_QUESTION + random.randint(0, 3)
    count_answers = COUNT_ANSWERS + random.randint(0, 3)
    count_quiz = COUNT_QUIZ + random.randint(0, 2)


    course= create_course(fake)
    author=random.choice(teachers).user
    course_db=Course(name=course['name'],description=course['description'],author=author)

    course_db.save()
    for _ in range(module_number):
        module=create_module(fake,course_db)
        module_db=Module(name=module['name'],course=module['course'])
        module_db.save()

        for _ in range(count_quiz):
            quiz_data=create_quiz(fake,count_question,count_answers)
            quiz=Quiz(name=quiz_data['quiz_name'],module=module_db,course=course_db)
            quiz.save()

            for question in quiz_data['questions']:
                q=Question(quiz=quiz,name=question['question_name'])
                q.save()

                for answer in question['answers']:
                    a=Answer(question=q,name=answer['answer_name'],is_correct=answer['is_correct'])
                    a.save()

        for _ in range(topic_number):
            topic=create_topic(fake,module_db)
            topic_db=Topic(name=topic['name'],module=topic['module'],content=topic['content'],image=topic['image'])
            topic_db.save()

print('Success!')



