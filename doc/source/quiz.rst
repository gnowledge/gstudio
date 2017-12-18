Quiz
====

1. Quiz Implementation

   1. New GSystemTypes

      -  QuizItemEvent
      -  QuizItemPost

   2. New AttributeTypes

      -  quizitem\_show\_correct\_ans. Type: bool
      -  quizitem\_problem\_weight. Type: float (0 to 100)
      -  quizitem\_max\_attempts. Type: int (0 to 5)
      -  quizitempost\_user\_given\_ans. basestring

   3. New RelationTypes

      -  clone\_of

2. Quiz Authoring

   1. Quiz:

      -  Collection of QuizItems

   2. QuizItem:

      -  QuizItem can be created as a part of Quiz and/or independently
      -  Attributes of QuizItem:

         -  quiz\_type
         -  correct\_ans
         -  options
         -  quizitem\_show\_correct\_ans
         -  quizitem\_problem\_weight
         -  quizitem\_max\_attempts

3. Quiz Announcing

   1. QuizItem announced as QuizItemEvent (type\_of: Page GST)

      -  QuizItemEvent

         -  content -- QuizItem's content
         -  correct\_ans -- QuizItem's correct\_ans
         -  options -- QuizItem's options
         -  quiz\_type -- QuizItem's quiz\_type
         -  quizitem\_show\_correct\_ans -- QuizItem's
            quizitem\_show\_correct\_ans
         -  quizitem\_problem\_weight -- QuizItem's
            quizitem\_problem\_weight
         -  quizitem\_max\_attempts -- QuizItem's
            quizitem\_max\_attempts

   2. Create RT 'clone\_of' for QuizItem and QuizItemEvent
   3. Thread for QuizItemEvent will be created.
   4. Setup Interaction settings for this Thread
   5. Posts for this thread will be member\_of QuizItemPost

4. Quiz Player

   1. Based on 'quiz\_type', setup widgets.

      -  Multi Choice - Checkbox
      -  Single Choice - Radio buttons
      -  Short Answer - Textbox

   2. After entering answer

      -  prompt button 'Check' to show whether entered ans is correct or
         not
      -  prompt button 'Show Answer', to show correct\_ans if
         quizitem\_show\_correct\_ans is set True

   3. Create GAttribute quizitempost\_user\_given\_ans with the
      QuizItemPost and user's enetered answer