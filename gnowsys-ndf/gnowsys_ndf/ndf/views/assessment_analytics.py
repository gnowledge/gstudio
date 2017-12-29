import json
import requests

def hit_qbank_request(url):
    result_set = []
    try:
        # print "\n\nurl: ",url
        req_obj =  requests.get(url,verify = False)
        status = req_obj.status_code
        result_set = req_obj.json()
    except Exception as hit_qbank_request_err:
        print "\nError Occurred in hit_qbank_request()", hit_qbank_request_err
        pass
    return result_set


def get_assessment_id(domain,bankId,assessmentsoffered_id):
    # print "\nassessmentsoffered_id: ", assessmentsoffered_id
    url = str(domain) + ":8080/api/v1/assessment/banks/"+str(bankId)+\
    "/assessmentsoffered/"+str(assessmentsoffered_id)
    assessmentId = None
    try:
        result_set = hit_qbank_request(url)
        assessmentId = result_set["assessmentId"]
    except Exception as get_assessment_id:
        print "\nError Occurred in get_assessment_id()", get_assessment_id
        pass
    return assessmentId
    
def get_assessment_items_count(domain, bankId, assessmentId):
    url = str(domain) + ":8080/api/v1/assessment/banks/"+str(bankId)+\
    "/assessments/"+str(assessmentId) + "/items"
    assessmentId = None
    result_set = hit_qbank_request(url)
    return len(result_set)

def items_count_from_asessment_offered(domain, bankId, assessmentsoffered_id):
    assessment_id = get_assessment_id(domain, bankId, assessmentsoffered_id)
    items_count = get_assessment_items_count(domain, bankId, assessment_id)
    return items_count

def user_results(domain,bankId,offeredId,guserId=None):
    url = str(domain) + ":8080/api/v1/assessment/banks/"+str(bankId)+\
    "/assessmentsoffered/"+str(offeredId)+"/results"
    result_set = []
    if guserId:
        url = url + "?agentId=" + str(guserId)
    result_set = hit_qbank_request(url)
    return result_set

def user_assessment_results(domain, guserId,bankId,offeredId):

    # Declarations
    attemptedCount = notapplicableCount = 0
    correctCount = incorrectCount =  0
    not_applicable_qtn_type_list = [
        "question-type%3Aqti-extended-text-interaction%40ODL.MIT.EDU",
        "question-type%3Aqti-choice-interaction-multi-select-survey%40ODL.MIT.EDU",
        "question-type%3Aqti-choice-interaction-survey%40ODL.MIT.EDU",
        "question-type%3Aqti-upload-interaction-audio%40ODL.MIT.EDU",
        "question-type%3Aqti-upload-interaction-generic%40ODL.MIT.EDU",
        "question-type%3Aqti-inline-choice-interaction-mw-fill-in-the-blank%40ODL.MIT.EDU",
        ]

    data_set = user_results(domain,bankId,offeredId,guserId)
    # print "\ndata_set: {0} ".format(data_set)

    for questions in data_set:
        try:
            # questions['questions'] is a list of dicts
            for assessmentItem in questions['questions']:
                try:
                    responded_flag = assessmentItem['responded']
                    if isinstance(responded_flag, bool):
                        # Check whether the user has attempted the question or not
                        if responded_flag:
                            attemptedCount += 1
                            if assessmentItem['genusTypeId'] in not_applicable_qtn_type_list:
                                notapplicableCount += 1
                                correctCount += 1
                            else:
                                if assessmentItem['isCorrect']:
                                    correctCount += 1
                                elif not assessmentItem['isCorrect']:
                                    incorrectCount += 1
                except Exception as correctness_err:
                    print "Error: {0}".format(correctness_err)
                    pass
                countDict = {
                                "Attempted": attemptedCount,
                                "Correct": correctCount,
                                "Incorrect" : incorrectCount,
                                "NotApplicable":notapplicableCount
                            }

        except Exception as failed_to_fetch_user_data:
            print "Error: {0}".format(failed_to_fetch_user_data)
            pass
        print "\ncountDict: {0}".format(countDict)
        return countDict

# d = questionCount('https://103.36.84.149', '2','assessment.Bank%3A57e26c92b3fcec4c84a63f27%40ODL.MIT.EDU','assessment.AssessmentOffered%3A58f46bdbd09eca03d7364f1b%40ODL.MIT.EDU')
# print "*"*80
# print d