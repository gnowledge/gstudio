# What is Moodle?
Moodle is a Learning Management System with a goal to give teachers and students the required tools to teach and learn. It can be used to support any style of teaching and learning.

# Moodle Backup File
A Moodle Backup File (.mbz) is a compressed archive of a Moodle course that can be used to restore a course within Moodle which preserves course contents, structure and settings, but does not include student work or grades.
This file can be used to restore a course on Moodle.

## What is included?

A moodle backup file includes :
- Resources (Files, Folders etc.)
- Activities (Assignments, Quizzes and Quiz questions)
- Settings (Course Format, Theme, Course Completion settings, settings for Assignments and Quizzes)

It does **not include** :
- Student Enrollment
- Groups
- Guest Access Settings
- Contributions to Collaborative Activities made by any course member

# Using and creating a .mbz file

- FOR EXTRACTING 
	- `tar -xvzf moodle_backup.mbz`
 
- FOR ZIPPING INTO .mbz  
	- `cd folder1` , where folder1 is the folder containing all contents
   	- `tar -czvf <any_name>.mbz ./* `

# Structure of the .mbz file
A moodle course has several sections (or topics) which further has modules inside it. Modules/activities can be of various types- resources, ebooks etc.

There are four main directories which are - activities, course, files and sections.

The files which are the most important are - 

- **moodle_backup.xml** : This is the main file which describes various versions, course metadata like name, id, etc, titles, links to activities and sections as well as the settings used in a moodle course. 
- **sections/section_{id}/section.xml** : This describes a section in the moodle course which contains id, number, name, summary, timemodified and availability json.
- **course/course.xml** : This file describes a course, course name, id, summary, startdate, enddate, coursedisplay, category etc.
- **activities/{activity_type}_{id}/inforef.xml** :  This has the file IDs which refer to the files.xml file
- **activities/{activity_type}_{id}/module.xml** : This contains the module data like module name in the section, module id and other settings related to it.
- **activites/{activity_type}_{id}/resource.xml** :  This describes the name, displayoptions, timemodified, etc for the resource in an activity.
- **files.xml** : This is a very important file, which links all the media content and text content together. It contains a lot of file tags with their ids which refer to type of the component, context id, time modified, source, filepath, filenames, author, content hash, mimetype, itemid, etc.

To store a file, file is renamed as its SH1 hash (found using BASH command `sha1sum filename.ext`). And, file is stored in files/ a folder with name as first two letters of the hash. e.g. If hash of file is d3614f1cb8df5a00faaf805b5be7670ddfbebbb5 , It is stored as files/d3/d3614f1cb8df5a00faaf805b5be7670ddfbebbb5

Kindly check the complete file structure for more details and other files.

A python script `convert.py` was written to create these xml files to embed an epub that was generated on CLIx Server into a moodle course. The mbz file was created after creating these xmls and zipping them together and then the mbz was restored on Moodle.

Hence, the process can be summarised as-
1. Running the script
2. Zipping the file into an .mbz format
3. "Restoring" on Moodle


Note that this was tested on the demo moodle website- https://demo.moodle.net  with a teacher login.