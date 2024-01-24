# <a href="https://grammar.pl">Grammar.pl</a>

The website is dedicated to Polish high school graduates. Everyone can prepare for the baccalaureate by solving tests from previous years. The tests are interactive and pleasant to learn. The tests are divided into sections. Users can also create their own tasks, rate others' tasks, and comment. They have their own profiles with activity on the site. The site is based on django.

<div align="center">
<img src="demo.gif" alt="Gif presenting the website"/>
</div>

# What is this about?
This website is intended for Polish students who are preparing for the English language school-leaving exam in the Polish high-school. It contains a set of examination tasks at all available levels of this exam. It allows to solve tasks interactively and immediately check the correctness of the answers. There is also a possibility to create one's own tasks, as well as to rate other people's tasks. The website allows you to comment other people tasks and respond to the comments of other people. Users can customize their profile and view other people activities on the site.

## Which English language school-leaving exams can be found on the website?
On the website you can find the May school-leaving exams from 2015 to 2019 at all three levels (basic, extended and bilingual).

## What else is available on the site except English language school-leaving exams?
The website also contains a whole section on learning different language tenses. The community can add their own tasks there and assess the tasks of others.

## Do I have to register?
No, you do not have to register until you want to add new tasks and comment on others' tasks.

### Additional note
It's my first django project ever 😊

## How to run?
1. Fill in data in .env file
2. Install Docker:
   * Windows/Mac: Install Docker Desktop.
   * Linux: Install Docker Engine and Docker Compose using your distro's package manager.
3. You should build the image with command:
   > docker-compose build
4. You can run the application using command:
   > docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

Default admin credentials for this key are:
- **login**: admin
- **password**: grammar_pl