from plattform.models import Subscriber,Got,QuizResult
import random
subscribers=Subscriber.objects.all()

print('Started...')
for subscriber in subscribers:
    course= subscriber.course
    modules=course.modules.all()

    quizes=course.quizes.all()

    all_topics=[]


    for module in modules:
        topics=module.topics.all()
        all_topics.extend(topics)

    for topic in all_topics:
        random_true=random.randint(0,1)

        if random_true:
            Got(topic=topic,subscriber=subscriber,got=True).save()
        else:
            Got(topic=topic,subscriber=subscriber,got=False).save()

    for quiz in quizes:
        questions_number=quiz.questions.count()
        total_points=0
        user_points=0
        for _ in range(questions_number):
            random_true=random.randint(0,1)

            if random_true:
                total_points+=1
                user_points+=1
            else:
                total_points+=1
        progress=round((user_points*100)/total_points)
        QuizResult(quiz=quiz,module=quiz.module,subscriber=subscriber,result=progress,course=course).save()
print('End!')