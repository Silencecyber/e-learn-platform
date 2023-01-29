This project is a kind of ONLINE PLATFORM for learning. Imagine some kind of school, for example, an English language school, so it has its own platform where you can also study additionally in addition to basic classes.
The terms specific to this project will be used below, so I will briefly describe what each means.
A course is a huge topic in a particular area.
A module is a component of the course.
Topic - component of the module.
Quiz - test within the module
For a better understanding of the structure, I will give an example.
Conditionally there is a course "English B1", it has a module "Grammar", in this module there are several topics: "Past Simple", "Present Perfect" and within the "Grammar" module there are some quizzes in which understanding of the entire module is checked

There are 3 types of users on the platform:

1.Superuser


2.Teacher


3.Student


What can a teacher do?
1. See general statistics, various graphs showing various kinds of information, such as which course is the most popular, the ratio of students to teachers, etc.
2. Create "colleagues" for yourself, but for security reasons, cannot delete them, to prevent accidental or deliberate deletion of all "staff" along with all the content of this teacher - a situation that only a superuser can fix.
3. Create students accounts, delete students, change their password.
4. Create courses, modules, topics, quizzes, all this can be edited and deleted (only your own)
5. Enroll students in a particular course, can expel him from there.
6. View the progress log for a particular course, see graphs showing the most "successful" student, can view detailed information about the course progress of a particular student, what topics he passed, what quizzes he passed, how many points, etc.
 
What can a student do?
1. See the list of courses for which he is enrolled.
2. Go to these courses, see modules, topics
3. View a list of his classmates regarding his course.
4. Pass quizzes, look at his progress regarding each course, which topics are passed, which quizzes, how many points
5. Edit information on its profile, change its password.

What can the superuser do?


The superuser can do everything that a regular teacher can do, but he has no restrictions regarding the authorship of a particular course, he can view, edit, delete, create any materials, he can delete teachers. It can also get into the site admin panel if it is enabled.

The database structure of this project will be presented below with a description, without taking into account the pre-installed django models.

 ![image](https://user-images.githubusercontent.com/96882434/215338423-5f375910-05e2-4c28-aa8b-3ffe1a4447ad.png)

The interactive structure can be viewed [here](
https://dbdiagram.io/d/63d16d5f296d97641d7c1cf8)

Brief description of models:

**Profile** - a model that describes the user's profile.


**Subscriber** - a model describing the subscriber of the course.


**Course** - a model describing a course.


**Module** - a model that describes the module of the course.


**Topic** - a model describing the module's topic.


**Got** -  a model that was created to monitor whether a topic is understood by a student.


**Quiz** - a model describing a quiz.


**Question** - a model describing a quiz question.


**Answer** - a model describing the answer to the question.


**QuizResult** - a model describing the result of a completed quiz.



Technology stack:


Backend: Python(Django),SQLite.


Frontend: HTML,CSS,JS,JQuery,Bootstrap,Highcharts,Webflow.



A brief demo of the platform functionality can be viewed [here](
https://www.youtube.com/watch?v=8ckpOgUwmGA)

