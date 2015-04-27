[![Code Health](https://landscape.io/github/Retzudo/taskstack/master/landscape.svg?style=flat)](https://landscape.io/github/Retzudo/taskstack/master)
[![Build Status](https://travis-ci.org/Retzudo/taskstack.svg?branch=master)](https://travis-ci.org/Retzudo/taskstack)
[![Coverage Status](https://coveralls.io/repos/Retzudo/taskstack/badge.svg?branch=master)](https://coveralls.io/r/Retzudo/taskstack?branch=master)
Look at all the badges. *LOOK AT THEM ಠ_ಠ*.

Taskstack
=========
Taskstack is (going to be) a really simple web app for task management.

The concept of Taskstack is dead simple
----------------------------------------
1. You have a group of people
2. One or more people in that group can assign tasks to members of the group
3. Every assignee has personal FIFO (first in, first out) queue of tasks.

Why?
----
The idea of Taskstack was born from my personal expierences. A group leader assigned task after task to a small team of 3 people and the number of tasks grew out of hand. The tasks were shifted around and priorities changed almost on an hourly basis. The group also used a plethora of tools. When it came to task management, we had an issue tracking system, mails, verbal conversations and two instant messaging systems. The end result was poorly done tasks and tasks that were simply never finished. My first idea was centralize all tasks and to buy those old fashioned "paper skewers" you would put small notes on. The group leader would then physically see the list of tasks of a person and maybe hesitate before putting another note on the pile. This in turn would keep the stack of notes manageable, in one place and the assignee in a happy mood. The problem with this approach is the note at the very bottom you'll probably never reach. That's why we need a queue. 

Terms
-----
### Group
A group of people who work together - duh.
### Member
A single member of the group - duh 2x.
### Assignee
A member of the group with a task queue. Members are always assignees. Assignees can add tasks to their own queue and the taskmaster will be notified of this event.
### Taskmaster
An assignee who can create new tasks and/or assign them to other members or themself.
### Task
A thing that needs to be done.
### Queue
A first in, first out queue of tasks assigned to an assignee. An assignee might have more than one queue while still respecting rule #1 below, not sure yet.

These are the rules that Taskstack establishes
----------------------------------------------
1. Each member of the group can only work on **one task at a time**. 
2. A task can **never be put back** in the queue once it has been worked on. Neither to where it was taken from, nor at the back of the queue. It can **only be paused or finished**.
3. Before adding a task to a queue, the taskmaster must always be presented with a **visualization of the assignees queue**. The act of assigning a task must be as visible as possible. No anonymous dropdown menus with lists of assignees. **Drag & drop mechanics are recommended**. I'm almost inclined to say *make it a chore*.
4. Each queue has a **limited number of tasks** it can hold (ideally <10).
5. Queues or assignees must be **colour-coded** according to the size of the queue (e. g. green = 2 tasks, yellow = 4 tasks, red = 7 tasks). Watch out for colour blindness though. People with achromatopsia (total colour blindness) may have a hard time seeing the difference between the colours you choose so maybe incorporate some some background pattern. 
6. To give people stuff to do you must use this tool and **only this tool**. No "could you quickly do this and that" or mails without a task in the queue. If as an assignee you get a task by mail, make a task in Taskstack and add it to your own queue.
7. A single task can be of **any complexity**. Based on that, it's the **taskmaster's job** to manage and distribute tasks evenly and fairly.
8. As a taskmaster you can only **remove tasks from anywhere within a queue** or add tasks **at the back of the queue**. If a task was removed and the same task is added again later by the taskmaster, the assignee will have to **confirm that action** (to prevent priority cheating, see 11.). 
9. When an assignee adds a task to their own queue, the taskmaster must confirm this.
10. Taskmasters will be **notified of changes to queues** that were made by their assignee. Assignees will be notified of changes to their queue that weren't made by themselves.
11. **No priorities**. The only form of priority implicitly stems from the order tasks are in a queue.

The gist is...
--------------
- The structure of queues and task must be simple (not talking about task complexity).
- The taskmaster is in charge of tasks.
- Once a task is in a queue, it *will* be worked on no matter what.
- Assigning tasks *must* be visualized.

Why did you call it 'Taskstack' when it's clearly a queue dummy!
----------------------------------------------------------------
Taskqueue sounds and looks weird. I mean look at it--'Queue'! Just a weird word. That's the only reason. I imagine it as a stack of notes on one's desk.

Web interface
-------------
Imagine something a little like Trello. As a taskmaster you can switch between groups and see all of its assignees and their queues. Unassigned tasks will have a special place from where they can be assigned. You can also remove tasks from any queue but not set a task as "Doing". That's something an assignee needs to do on their own.

As an assignee you can only see your own queue, remove tasks, mark your current task as done and set the next task as your current task.

Technical side of things
========================
Python
------
Python 3 is the way to go here. It's also recommended to use virtualenv to install the things listed in `requirements.txt` using pip. It doesn't matter to Python or Django where exactly you put the virtualenv but I suggest to just create it in the directory you cloned the repo to since the directory `venv/` is already in `.gitignore`. Here's the basic procedure:

```
$ cd taskstack
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Docker
------
There's a script for starting a PostgreSQL Docker container that works for default values in `settings.py`.

Django
------
While developing, you should run Django with `manage.py runserver`. DB host, DB name, username and password default to `localhost` and `taskstack` and can be changed by running Django with env variables (see `settings.py`). Docker, Gunicorn and nginx will be involved in the future but we'll figure out the magic later.

Ubuntu
------
On Ubuntu you need to install `libpq-dev` to be able to install `psycopg2` with pip.

Arch Linux
----------
On Arch you need to install `postgresql-libs`

Windows
-------
So you decided to develop on Windows? May the FSM have mercy on your twisted soul...

Well first of all, you'll need PostgreSQL. I suggest you [PostgreSQL Portable](http://sourceforge.net/projects/postgresqlportable/) because much like Docker, it doesn't litter your system with files. Start PostreSQL Portable and execute these commands to create a user and a database:
```SQL
CREATE USER taskstack WITH PASSWORD 'taskstack';
CREATE DATABASE taskstack;
GRANT ALL PRIVILEGES ON DATABASE taskstack TO taskstack;
ALTER USER taskstack CREATEDB; -- needed for test databases
```

Secondly, you cannot use pip to install `psycopg2` because you can't compile stuff on Windows without having Visual Studio set up and what not. So, create a regular virtualenv and install every requirement in `requirements.txt` via pip except `psycopg2`. To install `psycopg2` you need to download a precompiled wheel file from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#psycopg) (take the 32-bit version for Python 3.4, the 64-bit version didn't work for me and it shouldn't make any difference). Now install that file with `pip install that-wheel-file.whl`. Everything should be set up now and you should be able to run `python taskstack\manage.py test core`.
