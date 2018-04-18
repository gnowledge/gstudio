GNOWSYS Studio
==============

GNOWSYS Studio (gStudio for short) is an online platform for
collaboration that supports maintaining electronic publishing and
curation of resources (online file management), online discussion,
content management, group and task management, event management, create
and play online courses, information management, semantically link all
published resources, visualize graphs, analytics, user rating etc.

The platform is best suited for a collaborative online academy.

The platform is still under active development. The platform is deployed
for varying purposes at the following sites:

-  http://nroer.gov.in: used as a digital curated Repository of Open
   Educational Resources.
-  https://staging-clix.tiss.edu: Used as a online Course maker (CMS),
   Course player (LMS) with analytics, Formative and Summative
   Assessments, Survey, Buddy login (multiple users at each terminal)
   and embeddable HTML5 Apps (Interactives, Games and Simulations).
   Suitable for offline and online use for computer based education.
-  https://abcde.metastudio.org: used as a Personal and a Collaborative
   Workspaces with Topic Map creator, Activity organizer, Forum/Blog and
   Digital Library with rating, feedback and feeds.

Deppending on the need, it is possible to configure an instance with all
the three above uses in a single site.

Gnowledge lab of Homi Bhabha Centre for Science Education, TIFR develops
and maintains gStudio as its flagship software development project for
supporting online education in collaboration with TISS, MIT and CIET,
NCERT.

Interoperable interfaces with REST bridge are work in progress to make
GStudio work with platforms that support OSID (http://osid.org/). A
python binding of DLKit (http://dlkit-doc.readthedocs.io/en/latest/) is
being used in collaboration with Office of the Digital Learning at MIT.


Platform Design
===============

The platform is designed around Users, Workspaces and Apps to make and
publish digital resources.

Users
-----

As a platform for collaboration, the most essential resource is a group
of users called **collaborators**. Users can join the platform with (for
online use) or without (for offline use) an email address.

Each user is provided with a personal workspace to create resources of
various kinds. See below about the kind of resources users can create
using special Apps.

Workspace
---------

A Workspace is a virtual desktop for collaboration among a group of
users. It is possible to create public or private workspaces which can
be moderated.

A parent workspace may have one or more sub-workspaces in a nested form.

Users of a workspace can create resources of various kinds using Apps.
See below for the Apps list.

Workspace members are always a subset of the registered users of the
platform.

Workspaces are the basic design feature of GStudio which can be
transformed into any of the following:

-  Course player (LMS)
-  Course maker (CMS)
-  Digital Library (Topic Map organizer, Curriculum designer, Curation
   of Resources)
-  Collaborative online space
-  Online Survey/Polls
-  Programs (Fixed or Flexible duration)

Apps
----

Several Apps are provided to create and/or curate digital resources in
the workspaces to collaboratively constuct knowledge. The platform
supports the following Basic Apps:

-  Pages

   -  Wiki pages for collaboratively writing documents
   -  Blog pages for posting a view point followed by discussion
   -  Info pages for documentation such as Help, FAQ etc

-  Files:

   -  Uploaded as images, videos, audio files, word processing files,
      PDFs, HTML files and so on.
   -  Organized into folders/collections.

Using the basic Apps, Pages and Files, many varieties of Apps can be
derived. Curently, the platform supports the following derived Apps:

-  Forum for discussion to be integrated with a mailing list, Telegram.
-  Knowledge Organizer for maintaining a taxonomy of learning objectives
   into themes, topics, concepts, skills, competencies or outcomes.
-  Course Maker (CMS)
-  Course Player (LMS)
-  Notifications
-  Basic Quiz Builder

Upcoming Apps:
~~~~~~~~~~~~~~

-  Task Manager
-  Event Scheduler
-  Glossary
-  Concept mapping
-  Admin Studio

Deprecated Apps:
~~~~~~~~~~~~~~~~

-  Email Client
-  Local Messages
-  Meetings App linked to BigBlueButton
-  Collaborative editing using mobwrite
-  Bib\ :sub:`App`
-  MIS

Generic Features
----------------

The following features are inherited from the information architecture
of GStudio to all the Apps:

-  Tagging (Keywords)
-  Interactions
-  Rating
-  Search
-  Authentication
-  Authorization
-  History Management (version control)
-  Metadata
-  Translation
-  Notifications
-  API (for Read-only)
-  Responsive UI
-  Support for skins for UI
-  Data exchange (Import and Export)
-  csv processing for bulk uploads
-  Collection export into epub3 format
-  Benchmark for profiling Functions
-  d3 graphs
-  Email notifications
-  RSS feeds

Upcoming Generic Features:
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  CRUD API
-  Elastic Search
-  Telegram Bot
-  chat dB
-  Single Sign-on plugin
-  Data aggregation from offline sites
-  Aggregated analytics
-  OSM support
-  Annotation
-  OSID compliance
-  LTI compliance
-  Accessibility compliance
-  Adaptive Assessment
-  H5P support
-  OAT, OAC

   -  UI provision to add Folders in OAT.
   -  Authentication in OAT
   -  Assessment Analytics functions + UI
   -  New Assessment types

-  Badges implementation
-  Test cases
-  UI for History/Version