Taskstack
=========
The idea of Taskstack was born from my personal expierences. A group leader assigned task after task to a small team of 3 people and the number of tasks grew out of hand. The tasks were shifted around and priorities changed almost on an hourly basis. The group also used a plethora of tools. When it came to task management, we had an issue tracking system, mails, verbal conversation and two instant messaging systems. The end result was poorly done tasks and tasks that were simply never finished. My first idea was centralize all tasks and to buy those old fashioned "paper skewers" you would put small notes on. The group leader would then physically see the list of tasks of a person and maybe hesitate before putting another note on the pile. This in turn would keep the stack of notes manageable, in one place and the assignee in a happy mood. The problem with this approach is the note at the very bottom you'll probably never reach. That's why we need a queue. 

The concept of Taskstack is dead simple.
----------------------------------------
1. You have a group of people
2. One or more people in that group can assign tasks to members of the group
3. Every assignee has personal FIFO (first in, first out) queue of tasks.

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
1. Each member of the group can only work on one task at a time. 
2. A task can never be put back in the queue once it has been worked on. Neither to where it was taken from, nor at the back of the queue. It can only be paused or finished.
3. Before adding a task to a queue, the taskmaster must always be presented with a visualization of the assignees queue. The act of assigning a task must be as visible as possible. No anonymous dropdown menus with lists of assignees. Drag & drop mechanics are recommended. I'm almost inclined to say *make it a chore*.
4. Each queue has a limited number of tasks (ideally <10).
5. Queues or assignees must be colour-coded according to the size of the queue (e. g. green = 2 tasks, yellow = 4 tasks, red = 7 tasks).
6. To give people stuff to do you must use this tool and only this tool. No "could you quickly do this and that" or mails without a task in the queue. If as an assignee you get a task by mail, make a task in Taskstack and add it to your own queue.
7. A single task can be of any complexity. Based on that, it's the taskmaster's job to manage and distribute tasks evenly and fairly.
8. As a taskmaster you can only remove tasks from anywhere within a queue or add tasks at the back of the queue. If a task was removed and the same task is added again later, the assignee will have to confirm that action.
8. Taskmasters will be notified by changes to queues that were made by their assignee. Assignees will be notified by changes to their queue that weren't made by themselves.
9. No priorities. The only form of priority implicitly stems from the order tasks are in a queue.

Why did you call it 'Taskstack' when it's clearly a queue dummy!
----------------------------------------------------------------
Taskqueue sounds and looks weird. I mean look at it--'Queue'! Just a weird word. That's the only reason. I imagine it as a stack of notes on one's desk.
