import json
import requests
print "\n In assessment Analytics"
def userSpecificData(domain,bankId,offeredId,guserId=None):
    url = str(domain) + ":8080/api/v1/assessment/banks/"+str(bankId)+"/assessmentsoffered/"+str(offeredId)+"/results"
    data = []
    try:
        if guserId:
            url = url + "?agentId="+guserId
        print "\n\nurl: ", url
        r =  requests.get(url,verify = False)
        status = r.status_code
        # print "r.text, ", r.text
        data = r.json()
    except Exception as userSpecificData_err:
        print "\nError Occurred in userSpecificData()", userSpecificData_err
        pass
    return data

def questionCount(domain, guserId,bankId,offeredId):
    questionCount = 0
    visitedCount = 0
    attemptedCount = 0
    unattemptedCount = 0
    correctCount = 0
    incorrectCount = 0
    notapplicableCount = 0
    countDict = {}
    questionCountData = userSpecificData(domain,bankId,offeredId,guserId)
    # print "\nH: ", questionCountData
    for questions in questionCountData:
        if 'questions' in questions:
            question = questions['questions']
            for itemID in question:
                itemID['itemId']
                questionCount += 1
                '''
                This below If statement gives us the details of the no of question visited by student
                '''

                try:
                    if ((itemID ['responded'] == True) or (itemID ['responded'] == False)):
                        visitedCount += 1
                except:
                    print 'No Field Found'
                    pass
                
                '''
                This below If statements gives us the detials of if the student has responded to the question or not
                '''
                
                if (itemID['responded'] == True):
                    attemptedCount += 1
                elif (itemID['responded'] == False):
                    unattemptedCount +=1
        
                '''
                This below If statements gives us the detials of if the answers given by the students were correct or inCorrect 
                '''
                try:
                    if (itemID['genusTypeId'] == "question-type%3Aqti-extended-text-interaction%40ODL.MIT.EDU" 
                    and itemID['responded'] == True or  
                        itemID['genusTypeId'] == "question-type%3Aqti-choice-interaction-multi-select-survey%40ODL.MIT.EDU"
                    and itemID['responded'] == True or 
                        itemID['genusTypeId'] == "question-type%3Aqti-choice-interaction-survey%40ODL.MIT.EDU" 
                    and itemID['responded'] == True or
                        itemID['genusTypeId'] == "question-type%3Aqti-upload-interaction-audio%40ODL.MIT.EDU"
                    and itemID['responded'] == True or
                        itemID['genusTypeId'] == "question-type%3Aqti-upload-interaction-generic%40ODL.MIT.EDU"
                       ):
                        notapplicableCount += 1
                        correctCount += 1
                    else:
                        if (itemID['isCorrect'] == True):
                            correctCount += 1
                        else:
                            incorrectCount += 1
                except:
                    pass
    #               print "In this Assessment Nothing Was actually answered"

        return {"Question": questionCount,
                     "Visited" : visitedCount,
                     "Attempted": attemptedCount,
                     "Correct": correctCount,
                     "Incorrect" : incorrectCount,
                     "NotApplicable":notapplicableCount,
                      "Unattempted" : unattemptedCount
                     
                    }


# d = questionCount('https://103.36.84.149', '2','assessment.Bank%3A57e26c92b3fcec4c84a63f27%40ODL.MIT.EDU','assessment.AssessmentOffered%3A58f46bdbd09eca03d7364f1b%40ODL.MIT.EDU')
# print "*"*80
# print d