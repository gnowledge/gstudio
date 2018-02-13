The following document is deprecated. Please visit on 10th Feb 2018 for updated description.

**POINTS Multiplier factor**
- FILE UPLOAD POINTS = 25
- NOTE CREATE POINTS = 30
- QUIZ CORRECT POINTS = 5
- COMMENT POINTS = 5

--

username : user's username

COURSE
total_modules : No. of modules in the course
total_units : No. of units in the course
units_completed : No. of Units the user has completed.
		Completion is calculated on viewing/visiting the activities under a unit.
modules_completed : No. of Modules the user has completed. If all the units falling under a module are marked as
		completed, the module is then considered to be completed.
module_progress_meter : Completed Modules/ Total Modules
unit_progress_meter : Completed Units/ Total Units
===============================================================

FILES
user_files : No. of files uploaded by user
other_viewing_my_files : No. of other(unique) users who viewed user's files
total_rating_rcvd_on_files : Average of all user's files ratings. [(Sum of rating of 'N' files)/ 'N']
total_files_viewed_by_user : No. of other's files viewed by the user.
		If a single file is viewed more than once, it will be considered/counted as 1 file view.
===============================================================

NOTES
user_notes : No. of notes created by user
total_notes_read_by_user : No. of other's notes read by the user.
		If a single note is read more than once, it will be considered/counted as 1 note read.
total_rating_rcvd_on_notes : Average of all user's notes ratings [(Sum of rating of 'N' notes)/ 'N'].
others_reading_my_notes : No. of other(unique) users who read user's notes.
===============================================================

COMMENTS
total_cmnts_by_user : No. of comments the user has posted anywhere in the course.
cmnts_rcvd_by_user : No. of comments posted on user's notes and files by other users.
cmts_on_user_notes : No. of comments posted on user's notes by other users.
commented_on_others_notes : No. of notes(created by others) on which the user has commented.
commented_on_others_files : No. of files(uploaded by others) on which the user has commented.
unique_users_commented_on_user_files : No. of unique users who posted comments on user's uploaded files.
cmts_on_user_files : No. of comments posted on user's files by other users.
===============================================================

QUIZ
total_quizitems : No. of quiz present in the course
attempted_quizitems : No. of quiz the user has attempted.
incorrect_attempted_quizitems : No. of quiz the user has attempted with evaluation incorrect/wrong answer.
correct_attempted_quizitems : No. of quiz the user has attempted with evaluation correct/right answer.
===============================================================


Sample Course Structure:

Course_1:
	Module_1:
		Session_1:
			Unit_1
				Activity_1
				Activity_2
			Unit_2
				Activity_3
		Session_2:
			Unit_3
				Activity_4
			Unit_4
				Activity_5
	Module_2:
		Session_3:
			Unit_5
				Activity_6
		Session_4:
			Unit_6
				Activity_7



Module Completion Logic:

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

An Activity is one of the following:
	1. Page
		- requires viewing/visiting it to mark complete
	2. File
		- requires viewing/visiting it to mark complete
	3. Quiz
		- requires attempting it to mark complete
