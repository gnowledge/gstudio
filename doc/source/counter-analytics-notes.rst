Counter Analytics
=================

**POINTS Multiplier factor**
 - FILE UPLOAD POINTS = 25
 - NOTE CREATE POINTS = 30
 - QUIZ CORRECT POINTS = 5
 - COMMENT POINTS = 5

----

username : user's username

COURSE total\_modules : No. of modules in the course total\_units : No.
of units in the course units\_completed : No. of Units the user has
completed. Completion is calculated on viewing/visiting the activities
under a unit. modules\_completed : No. of Modules the user has
completed. If all the units falling under a module are marked as
completed, the module is then considered to be completed.
module\_progress\_meter : Completed Modules/ Total Modules
unit\_progress\_meter : Completed Units/ Total Units
===============================================================

FILES user\_files : No. of files uploaded by user
other\_viewing\_my\_files : No. of other(unique) users who viewed user's
files total\_rating\_rcvd\_on\_files : Average of all user's files
ratings. [(Sum of rating of 'N' files)/ 'N']
total\_files\_viewed\_by\_user : No. of other's files viewed by the
user. If a single file is viewed more than once, it will be
considered/counted as 1 file view.
===============================================================

NOTES user\_notes : No. of notes created by user
total\_notes\_read\_by\_user : No. of other's notes read by the user. If
a single note is read more than once, it will be considered/counted as 1
note read. total\_rating\_rcvd\_on\_notes : Average of all user's notes
ratings [(Sum of rating of 'N' notes)/ 'N']. others\_reading\_my\_notes
: No. of other(unique) users who read user's notes.
===============================================================

COMMENTS total\_cmnts\_by\_user : No. of comments the user has posted
anywhere in the course. cmnts\_rcvd\_by\_user : No. of comments posted
on user's notes and files by other users. cmts\_on\_user\_notes : No. of
comments posted on user's notes by other users.
commented\_on\_others\_notes : No. of notes(created by others) on which
the user has commented. commented\_on\_others\_files : No. of
files(uploaded by others) on which the user has commented.
unique\_users\_commented\_on\_user\_files : No. of unique users who
posted comments on user's uploaded files. cmts\_on\_user\_files : No. of
comments posted on user's files by other users.
===============================================================

QUIZ total\_quizitems : No. of quiz present in the course
attempted\_quizitems : No. of quiz the user has attempted.
incorrect\_attempted\_quizitems : No. of quiz the user has attempted
with evaluation incorrect/wrong answer. correct\_attempted\_quizitems :
No. of quiz the user has attempted with evaluation correct/right answer.
===============================================================

Sample Course Structure:

Course\_1: Module\_1: Session\_1: Unit\_1 Activity\_1 Activity\_2
Unit\_2 Activity\_3 Session\_2: Unit\_3 Activity\_4 Unit\_4 Activity\_5
Module\_2: Session\_3: Unit\_5 Activity\_6 Session\_4: Unit\_6
Activity\_7

Module Completion Logic:

::

    * When a user views Activity_1, Activity_2, Unit_1 is marked as 'Completed'
    * When a user views Activity_3, Unit_2 is marked as 'Completed'
        * When Unit_1 and Unit_2 are completed, Session_1 is marked as 'Completed'

    * When a user views Activity_4, Unit_3 is marked as 'Completed'
    * When a user views Activity_5, Unit_4 is marked as 'Completed'
        * When Unit_3 and Unit_4 is completed, Session_2 is marked as 'Completed'

    * When Session_1 and Session_2 are completed, Module_1 is complted

    NOTE: When a user views ONLY Activity_6 from Module_2, Unit_5 and Session_3 are marked as 'Completed'.
    But, since Activity_7 is not viewed, Unit_6 and Session_4 will be marked as 'Incomplete' and hence,
    Module_2 is also 'Incomplete'.

An Activity is one of the following: 1. Page - requires viewing/visiting
it to mark complete 2. File - requires viewing/visiting it to mark
complete 3. Quiz - requires attempting it to mark complete