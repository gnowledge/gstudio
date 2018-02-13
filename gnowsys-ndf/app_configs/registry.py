
MANAGER_PATHS = {

    'service': {
        'ASSESSMENT': ('dlkit.services.assessment.AssessmentManager',
                       'dlkit.services.assessment.AssessmentManager'),
        'ASSESSMENT_AUTHORING': ('dlkit.services.assessment_authoring.AssessmentAuthoringManager',
                                 'dlkit.services.assessment_authoring.AssessmentAuthoringManager'),
        'AUTHORIZATION': ('dlkit.services.authorization.AuthorizationManager',
                          'dlkit.services.authorization.AuthorizationManager'),
        'REPOSITORY': ('dlkit.services.repository.RepositoryManager',
                       'dlkit.services.repository.RepositoryManager'),
        'LEARNING': ('dlkit.services.learning.LearningManager',
                     'dlkit.services.learning.LearningManager'),
        'LOGGING': ('dlkit.services.logging_.LoggingManager',
                    'dlkit.services.logging_.LoggingManager'),
        'COMMENTING': ('dlkit.services.commenting.CommentingManager',
                       'dlkit.services.commenting.CommentingManager'),
        'RESOURCE': ('dlkit.services.resource.ResourceManager',
                     'dlkit.services.resource.ResourceManager'),
        'GRADING': ('dlkit.services.grading.GradingManager',
                    'dlkit.services.grading.GradingManager')
    },
    'mongo': {
        'ASSESSMENT': ('dlkit.mongo.assessment.managers.AssessmentManager',
                       'dlkit.mongo.assessment.managers.AssessmentProxyManager'),
        'ASSESSMENT_AUTHORING': ('dlkit.mongo.assessment_authoring.managers.AssessmentAuthoringManager',
                                 'dlkit.mongo.assessment_authoring.managers.AssessmentAuthoringProxyManager'),
        'AUTHORIZATION': ('dlkit.mongo.authorization.managers.AuthorizationManager',
                          'dlkit.mongo.authorization.managers.AuthorizationProxyManager'),
        'REPOSITORY': ('dlkit.mongo.repository.managers.RepositoryManager',
                       'dlkit.mongo.repository.managers.RepositoryProxyManager'),
        'LEARNING': ('dlkit.mongo.learning.managers.LearningManager',
                     'dlkit.mongo.learning.managers.LearningProxyManager'),
        'LOGGING': ('dlkit.mongo.logging_.managers.LoggingManager',
                    'dlkit.mongo.logging_.managers.LoggingProxyManager'),
        'COMMENTING': ('dlkit.mongo.commenting.managers.CommentingManager',
                       'dlkit.mongo.commenting.managers.CommentingProxyManager'),
        'RESOURCE': ('dlkit.mongo.resource.managers.ResourceManager',
                     'dlkit.mongo.resource.managers.ResourceProxyManager'),
        'GRADING': ('dlkit.mongo.grading.managers.GradingManager',
                     'dlkit.mongo.grading.managers.GradingProxyManager')
    },
    'gstudio': {
        'ASSESSMENT': ('dlkit.mongo.assessment.managers.AssessmentManager',
                       'dlkit.mongo.assessment.managers.AssessmentProxyManager'),
        # 'ASSESSMENT_AUTHORING': ('dlkit.mongo.assessment_authoring.managers.AssessmentAuthoringManager',
        #                          'dlkit.mongo.assessment_authoring.managers.AssessmentAuthoringProxyManager'),
        'AUTHORIZATION': ('dlkit_gstudio.authorization.managers.AuthorizationManager',
                          'dlkit_gstudio.authorization.managers.AuthorizationProxyManager'),
        'REPOSITORY': ('dlkit_gstudio.repository.managers.RepositoryManager',
                       'dlkit_gstudio.repository.managers.RepositoryProxyManager'),
        # 'LEARNING': ('dlkit.mongo.learning.managers.LearningManager',
        #              'dlkit.mongo.learning.managers.LearningProxyManager'),
        # 'LOGGING': ('dlkit.mongo.logging_.managers.LoggingManager',
        #             'dlkit.mongo.logging_.managers.LoggingProxyManager'),
        # 'COMMENTING': ('dlkit.mongo.commenting.managers.CommentingManager',
        #                'dlkit.mongo.commenting.managers.CommentingProxyManager'),
        # 'RESOURCE': ('dlkit.mongo.resource.managers.ResourceManager',
        #              'dlkit.mongo.resource.managers.ResourceProxyManager'),
        # 'GRADING': ('dlkit.mongo.grading.managers.GradingManager',
        #              'dlkit.mongo.grading.managers.GradingProxyManager')
    },

    'authz_adapter': {
        'ASSESSMENT': ('dlkit.authz_adapter.assessment.managers.AssessmentManager',
                       'dlkit.authz_adapter.assessment.managers.AssessmentProxyManager'),
        'ASSESSMENT_AUTHORING': ('dlkit.authz_adapter.assessment_authoring.managers.AssessmentAuthoringManager',
                                 'dlkit.authz_adapter.assessment_authoring.managers.AssessmentAuthoringProxyManager'),
        'AUTHORIZATION': ('dlkit.authz_adapter.authorization.managers.AuthorizationManager',
                          'dlkit.authz_adapter.authorization.managers.AuthorizationProxyManager'),
        'REPOSITORY': ('dlkit.authz_adapter.repository.managers.RepositoryManager',
                       'dlkit.authz_adapter.repository.managers.RepositoryProxyManager'),
        # 'REPOSITORY': ('dlkit_gstudio.repository.managers.RepositoryManager',
        #                'dlkit_gstudio.repository.managers.RepositoryProxyManager'),
        'LEARNING': ('dlkit.authz_adapter.learning.managers.LearningManager',
                     'dlkit.authz_adapter.learning.managers.LearningProxyManager'),
        'LOGGING': ('dlkit.authz_adapter.logging_.managers.LoggingManager',
                    'dlkit.authz_adapter.logging_.managers.LoggingProxyManager'),
        'COMMENTING': ('dlkit.authz_adapter.commenting.managers.CommentingManager',
                       'dlkit.authz_adapter.commenting.managers.CommentingProxyManager'),
        'RESOURCE': ('dlkit.authz_adapter.resource.managers.ResourceManager',
                     'dlkit.authz_adapter.resource.managers.ResourceProxyManager'),
        'GRADING': ('dlkit.authz_adapter.grading.managers.GradingManager',
                    'dlkit.authz_adapter.grading.managers.GradingProxyManager')
    },
    'time_based_authz': {
        'AUTHORIZATION': ('dlkit.stupid_authz_impls.time_based_authz.AuthorizationManager',
                          'dlkit.stupid_authz_impls.time_based_authz.AuthorizationProxyManager')
    },
    'ask_me_authz': {
        'AUTHORIZATION': ('dlkit.stupid_authz_impls.ask_me_authz.AuthorizationManager',
                          'dlkit.stupid_authz_impls.ask_me_authz.AuthorizationProxyManager')
    },
    'handcar': {
        'LEARNING': ('dlkit.handcar.learning.managers.LearningManager',
                     'dlkit.handcar.learning.managers.LearningProxyManager')
    },
    'aws_adapter': {
        'REPOSITORY': ('dlkit.aws_adapter.repository.managers.RepositoryManager',
                       'dlkit.aws_adapter.repository.managers.RepositoryProxyManager')
    },
    'qbank_authz': {
        'AUTHORIZATION': ('qbank_authz.authorization.managers.AuthorizationManager',
                          'qbank_authz.authorization.managers.AuthorizationProxyManager')
    },
    'roles_authz': {
        'AUTHORIZATION': ('roles_authz.authorization.managers.AuthorizationManager',
                          'roles_authz.authorization.managers.AuthorizationProxyManager')
    },
    'resource_agent_authz_adapter': {
        'RESOURCE': ('resource_agent_authz_adapter.managers.ResourceManager',
                     'resource_agent_authz_adapter.managers.ResourceProxyManager')
    },
}

