
try:
    from django.conf import settings
except ImportError:
    from ..dlkit_runtime_project import settings

from dlkit_runtime.handcar_configs import *
from dlkit_runtime.primordium import Type

def impl_key_dict(value, priority=1):
    """to reduce duplicate code in configs.py and handcar_configs.py"""
    return {
        'syntax': 'STRING',
        'displayName': 'Implementation Key',
        'description': 'Implementation key used by Runtime for class loading',
        'values': [
            {'value': value, 'priority': priority}
        ]
    }


AWS_ASSET_CONTENT_TYPE = Type(**
                              {
                              'authority': 'odl.mit.edu',
                              'namespace': 'asset_content_record_type',
                              'identifier': 'amazon-web-services'
                              })

###################################################
# PRODUCTION SETTINGS
###################################################

# HANDCAR_IMPL = settings.HANDCAR_IMPL
'''
AWS_ADAPTER_1 = {
    'id': 'aws_adapter_configuration_1',
    'displayName': 'AWS Adapter Configuration',
    'description': 'Configuration for AWS Adapter',
    'parameters': {
        'implKey': impl_key_dict('aws_adapter'),
        'cloudFrontPublicKey': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Public Key',
            'description': 'Public key for Amazon CloudFront service.',
            'values': [
                {'value': settings.CLOUDFRONT_PUBLIC_KEY, 'priority': 1}
            ]
        },
        'cloudFrontPrivateKey': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Private Key',
            'description': 'Private key for Amazon CloudFront service.',
            'values': [
                {'value': settings.CLOUDFRONT_PRIVATE_KEY, 'priority': 1}
            ]
        },
        'cloudFrontSigningKeypairId': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Signing Keypair ID',
            'description': 'Signing keypair id for Amazon CloudFront service.',
            'values': [
                {'value': settings.CLOUDFRONT_SIGNING_KEYPAIR_ID, 'priority': 1}
            ]
        },
        'cloudFrontSigningPrivateKeyFile': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Signing Private Key File',
            'description': 'Signing Private Key File for Amazon CloudFront service.',
            'values': [
                {'value': settings.CLOUDFRONT_SIGNING_PRIVATE_KEY_FILE, 'priority': 1}
            ]
        },
        'cloudFrontDistro': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Distro',
            'description': 'CloudFront Distr-o-bution.',
            'values': [
                {'value': settings.CLOUDFRONT_DISTRO, 'priority': 1}
            ]
        },
        'cloudFrontDistroId': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Distro Id',
            'description': 'CloudFront Distr-o-bution Id.',
            'values': [
                {'value': settings.CLOUDFRONT_DISTRO_ID, 'priority': 1}
            ]
        },
        'S3PrivateKey': {
            'syntax': 'STRING',
            'displayName': 'S3 Private Key',
            'description': 'Private Key for Amazon S3.',
            'values': [
                {'value': settings.S3_PRIVATE_KEY, 'priority': 1}
            ]
        },
        'S3PublicKey': {
            'syntax': 'STRING',
            'displayName': 'S3 Public Key',
            'description': 'Public Key for Amazon S3.',
            'values': [
                {'value': settings.S3_PUBLIC_KEY, 'priority': 1}
            ]
        },
        'S3Bucket': {
            'syntax': 'STRING',
            'displayName': 'S3 Bucket',
            'description': 'Bucket for Amazon S3.',
            'values': [
                {'value': settings.S3_BUCKET, 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
    }
}
'''

GSTUDIO_1 = {
    'id': 'gstudio_configuration_1',
    'displayName': 'Gstudio Configuration',
    'description': 'Configuration for Gstudio Implementation',
    'parameters': {
        'implKey': impl_key_dict('gstudio'),
        'mongoDBNamePrefix': {
            'syntax': 'STRING',
            'displayName': 'Mongo DB Name Prefix',
            'description': 'Prefix for naming mongo databases.',
            'values': [
                {'value': '', 'priority': 1}
            ]
        },
        'authority': {
            'syntax': 'STRING',
            'displayName': 'Mongo Authority',
            'description': 'Authority.',
            'values': [
                {'value': 'GSTUDIO', 'priority': 1}
            ]
        },
        'indexes': {
            'syntax': 'OBJECT',
            'displayName': 'Mongo DB Indexes',
            'description': 'Indexes to set in MongoDB',
            'values': [
                {'value': {}, 'priority': 1}
            ]
        },
        'mongoHostURI': {
            'syntax': 'STRING',
            'displayName': 'Mongo Host URI',
            'description': 'URI for setting the MongoClient host.',
            'values': [
                {'value': 'mongodb://localhost:27017', 'priority': 1}
            ]
        },
        # 'repositoryProviderImpl': {
        #     'syntax': 'STRING',
        #     'displayName': 'Repository Provider Implementation',
        #     'description': 'Implementation for repository service provider',
        #     'values': [
        #         {'value': 'AWS_ADAPTER_1', 'priority': 1}
        #     ]
        # },
        # 'assetContentRecordTypeForFiles': {
        #     'syntax': 'TYPE',
        #     'displayName': 'Asset Content Type for Files',
        #     'description': 'Asset Content Type for Records that store Files in a repository',
        #     'values': [
        #         {'value': AWS_ASSET_CONTENT_TYPE, 'priority': 1}
        #     ]
        # },
        # 'recordsRegistry': {
        #     'syntax': 'STRING',
        #     'displayName': 'Python path to the extension records registry file',
        #     'description': 'dot-separated path to the extension records registry file',
        #     'values': [
        #         {'value': 'records.registry', 'priority': 1}
        #     ]
        # },
        # 'learningProviderImpl': {
        #     'syntax': 'STRING',
        #     'displayName': 'Learning Provider Implementation',
        #     'description': 'Implementation for learning service provider',
        #     'values': [
        #         {'value': HANDCAR_IMPL, 'priority': 1}
        #     ]
        # },
        'keywordFields': {
            'syntax': 'OBJECT',
            'displayName': 'Keyword Fields',
            'description': 'Text fields to include in keyword queries',
            'values': [
                {'value': {}, 'priority': 1}
            ]
        },
        # shuffle choices of MCQs
        # 'magicItemLookupSessions': {
        #     'syntax': 'STRING',
        #     'displayName': 'Which magic item lookup sessions to try',
        #     'description': 'To handle magic IDs.',
        #     'values': [
        #         {'value': 'records.fbw_dlkit_adapters.multi_choice_questions.randomized_questions.RandomizedMCItemLookupSession', 'priority': 1}
        #     ]
        # },
        # 'magicAssessmentPartLookupSessions': {
        #     'syntax': 'STRING',
        #     'displayName': 'Which magic assessment part lookup sessions to try',
        #     'description': 'To handle magic IDs.',
        #     'values': [
        #         {'value': 'records.fbw_dlkit_adapters.magic_parts.assessment_part_records.MagicAssessmentPartLookupSession', 'priority': 1}
        #     ]
        # },
        'localImpl': {
            'syntax': 'STRING',
            'displayName': 'Implementation identifier for local service provider',
            'description': 'Implementation identifier for local service provider.  Typically the same identifier as the Mongo configuration',
            'values': [
                # {'value': 'AUTHZ_ADAPTER_1', 'priority': 1}
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
    }
}

ASK_ME_AUTHZ = {
    'id': 'stupid_authz_impl',
    'displayName': 'Stupid Authz Impl Configuration',
    'description': 'Configuration for Stupid Authorization Impl',
    'parameters': {
        'implKey': impl_key_dict('ask_me_authz'),
    }
}

QBANK_AUTHZ = {
    'id': 'qbank_authz_impl',
    'displayName': 'QBank Authz Configuration',
    'description': 'Configuration for QBank Authz Impl',
    'parameters': {
        'implKey': impl_key_dict('qbank_authz'),
    }
}

ROLES_AUTHZ = {
    'id': 'roles_authz_impl',
    'displayName': 'MIT ROLES Authz Configuration',
    'description': 'Configuration for MIT ROLES Authz Impl',
    'parameters': {
        'implKey': impl_key_dict('roles_authz'),
    }
}

RESOURCE_AGENT_AUTHZ_ADAPTER_1 = {
    'id': 'resource_agent_authz_adapter_configuration_1',
    'displayName': 'AuthZ Adapter Configuration',
    'description': 'Configuration for AuthZ Adapter',
    'parameters': {
        'implKey': impl_key_dict('resource_agent_authz_adapter'),
        'authzAuthorityImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'resourceProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Resource Provider Implementation',
            'description': 'Implementation for resource service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
    }
}

AUTHZ_ADAPTER_1 = {
    'id': 'authz_adapter_configuration_1',
    'displayName': 'AuthZ Adapter Configuration',
    'description': 'Configuration for AuthZ Adapter',
    'parameters': {
        'implKey': impl_key_dict('authz_adapter'),
        'authzAuthorityImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
        # Use MIT AssessmentAuthoring Provider for OEA Tool Integration Task
        'assessment_authoringProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Authoring Provider Implementation',
            'description': 'Implementation for assessment authoring service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'authorizationProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Authorization Provider Implementation',
            'description': 'Implementation for authorization service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        # LO of GSTUDIO
        'learningProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Learning Provider Implementation',
            'description': 'Implementation for learning service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
        'commentingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Commenting Provider Implementation',
            'description': 'Implementation for commenting service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'resourceProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Resource Provider Implementation',
            'description': 'Implementation for resource service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'gradingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Grading Provider Implementation',
            'description': 'Implementation for grading provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'loggingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Logging Provider Implementation',
            'description': 'Implementation for logging provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
    }
}

AUTHZ_ADAPTER_2 = {
    'id': 'authz_adapter_configuration_2',
    'displayName': 'AuthZ Adapter Configuration',
    'description': 'Configuration for AuthZ Adapter',
    'parameters': {
        'implKey': impl_key_dict('authz_adapter'),
        'authzAuthorityImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'ROLES_AUTHZ', 'priority': 1}
            ]
        },
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'learningProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Learning Provider Implementation',
            'description': 'Implementation for learning service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'AWS_ADAPTER_1', 'priority': 1}
            ]
        },
        'commentingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Commenting Provider Implementation',
            'description': 'Implementation for commenting service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'resourceProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Resource Provider Implementation',
            'description': 'Implementation for resource service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'gradingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Grading Provider Implementation',
            'description': 'Implementation for grading provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
    }
}


SERVICE = {
    'id': 'dlkit_runtime_bootstrap_configuration',
    'displayName': 'DLKit Runtime Bootstrap Configuration',
    'description': 'Bootstrap Configuration for DLKit Runtime',
    'parameters': {
        'implKey': impl_key_dict('service'),
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'AUTHZ_ADAPTER_1' , 'priority': 1}
            ]
        },
        'assessment_authoringProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Authoring Provider Implementation',
            'description': 'Implementation for assessment authoring service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'authorizationProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Authorization Provider Implementation',
            'description': 'Implementation for authorization service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'learningProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Learning Provider Implementation',
            'description': 'Implementation for learning service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'AUTHZ_ADAPTER_1', 'priority': 1}
                # {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
        'commentingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Commenting Provider Implementation',
            'description': 'Implementation for commenting service provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'resourceProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Resource Provider Implementation',
            'description': 'Implementation for resource service provider',
            'values': [
                {'value': 'RESOURCE_AGENT_AUTHZ_ADAPTER_1', 'priority': 1}
            ]
        },
        'gradingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Grading Provider Implementation',
            'description': 'Implementation for grading provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
        'loggingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Logging Provider Implementation',
            'description': 'Implementation for logging provider',
            'values': [
                {'value': 'MONGO_1', 'priority': 1}
            ]
        },
    }
}

BOOTSTRAP = {
    'id': 'bootstrap_configuration',
    'displayName': 'BootStrap Configuration',
    'description': 'Configuration for Bootstrapping',
    'parameters': {
        'implKey': impl_key_dict('service'),
    }
}

###################################################
# TEST SETTINGS
###################################################
'''
TEST_AWS_ADAPTER_1 = {
    'id': 'aws_adapter_configuration_1',
    'displayName': 'AWS Adapter Configuration',
    'description': 'Configuration for AWS Adapter',
    'parameters': {
        'implKey': impl_key_dict('aws_adapter'),
        'cloudFrontPublicKey': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Public Key',
            'description': 'Public key for Amazon CloudFront service.',
            'values': [
                {'value': settings.CLOUDFRONT_PUBLIC_KEY, 'priority': 1}
            ]
        },
        'cloudFrontPrivateKey': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Private Key',
            'description': 'Private key for Amazon CloudFront service.',
            'values': [
                {'value': settings.CLOUDFRONT_PRIVATE_KEY, 'priority': 1}
            ]
        },
        'cloudFrontSigningKeypairId': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Signing Keypair ID',
            'description': 'Signing keypair id for Amazon CloudFront service.',
            'values': [
                {'value': settings.CLOUDFRONT_SIGNING_KEYPAIR_ID, 'priority': 1}
            ]
        },
        'cloudFrontSigningPrivateKeyFile': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Signing Private Key File',
            'description': 'Signing Private Key File for Amazon CloudFront service.',
            'values': [
                {'value': settings.CLOUDFRONT_SIGNING_PRIVATE_KEY_FILE, 'priority': 1}
            ]
        },
        'cloudFrontDistro': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Distro',
            'description': 'CloudFront Distr-o-bution.',
            'values': [
                {'value': 'd1v4o60a4yrgi8.cloudfront.net', 'priority': 1}
            ]
        },
        'cloudFrontDistroId': {
            'syntax': 'STRING',
            'displayName': 'CloudFront Distro Id',
            'description': 'CloudFront Distr-o-bution Id.',
            'values': [
                {'value': 'E1OEKZHRUO35M9', 'priority': 1}
            ]
        },
        'S3PrivateKey': {
            'syntax': 'STRING',
            'displayName': 'S3 Private Key',
            'description': 'Private Key for Amazon S3.',
            'values': [
                {'value': settings.S3_PRIVATE_KEY, 'priority': 1}
            ]
        },
        'S3PublicKey': {
            'syntax': 'STRING',
            'displayName': 'S3 Public Key',
            'description': 'Public Key for Amazon S3.',
            'values': [
                {'value': settings.S3_PUBLIC_KEY, 'priority': 1}
            ]
        },
        'S3Bucket': {
            'syntax': 'STRING',
            'displayName': 'S3 Bucket',
            'description': 'Bucket for Amazon S3.',
            'values': [
                {'value': settings.S3_TEST_BUCKET, 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'TEST_MONGO_1', 'priority': 1}
            ]
        },
    }
}

TEST_MONGO_1 = {
    'id': 'mongo_configuration_1',
    'displayName': 'Mongo Configuration',
    'description': 'Configuration for Mongo Implementation',
    'parameters': {
        'implKey': impl_key_dict('mongo'),
        'mongoDBNamePrefix': {
            'syntax': 'STRING',
            'displayName': 'Mongo DB Name Prefix',
            'description': 'Prefix for naming mongo databases.',
            'values': [
                {'value': 'test_', 'priority': 1}
            ]
        },
        'authority': {
            'syntax': 'STRING',
            'displayName': 'Mongo Authority',
            'description': 'Authority.',
            'values': [
                {'value': settings.DLKIT_AUTHORITY, 'priority': 1}
            ]
        },
        'mongoHostURI': {
            'syntax': 'STRING',
            'displayName': 'Mongo Host URI',
            'description': 'URI for setting the MongoClient host.',
            'values': [
                {'value': settings.MONGO_HOST_URI, 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'TEST_AWS_ADAPTER_1', 'priority': 1}
            ]
        },
        # 'assetContentRecordTypeForFiles': {
        #     'syntax': 'TYPE',
        #     'displayName': 'Asset Content Type for Files',
        #     'description': 'Asset Content Type for Records that store Files in a repository',
        #     'values': [
        #         {'value': AWS_ASSET_CONTENT_TYPE, 'priority': 1}
        #     ]
        # },
    }
}

TEST_ASK_ME_AUTHZ = {
    'id': 'stupid_authz_impl',
    'displayName': 'Stupid Authz Impl Configuration',
    'description': 'Configuration for Stupid Authorization Impl',
    'parameters': {
        'implKey': impl_key_dict('ask_me_authz'),
    }
}

TEST_QBANK_AUTHZ = {
    'id': 'qbank_authz_impl',
    'displayName': 'QBank Authz Configuration',
    'description': 'Configuration for QBank Authz Impl',
    'parameters': {
        'implKey': impl_key_dict('qbank_authz'),
    }
}

TEST_RESOURCE_AGENT_AUTHZ_ADAPTER_1 = {
    'id': 'resource_agent_authz_adapter_configuration_1',
    'displayName': 'AuthZ Adapter Configuration',
    'description': 'Configuration for AuthZ Adapter',
    'parameters': {
        'implKey': impl_key_dict('resource_agent_authz_adapter'),
        'authzAuthorityImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'TEST_QBANK_AUTHZ', 'priority': 1}
            ]
        },
        'resourceProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Resource Provider Implementation',
            'description': 'Implementation for resource service provider',
            'values': [
                {'value': 'TEST_MONGO_1', 'priority': 1}
            ]
        },
    }
}

TEST_AUTHZ_ADAPTER_1 = {
    'id': 'authz_adapter_configuration_1',
    'displayName': 'AuthZ Adapter Configuration',
    'description': 'Configuration for AuthZ Adapter',
    'parameters': {
        'implKey': impl_key_dict('authz_adapter'),
        'authzAuthorityImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'TEST_MONGO_1', 'priority': 1}
            ]
        },
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'TEST_MONGO_1', 'priority': 1}
            ]
        },
        'assessment_authoringProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Authoring Provider Implementation',
            'description': 'Implementation for assessment authoring service provider',
            'values': [
                {'value': 'TEST_MONGO_1', 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'TEST_AWS_ADAPTER_1', 'priority': 1}
            ]
        },
        'commentingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Commenting Provider Implementation',
            'description': 'Implementation for commenting service provider',
            'values': [
                {'value': 'TEST_MONGO_1', 'priority': 1}
            ]
        },
        'resourceProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Resource Provider Implementation',
            'description': 'Implementation for resource service provider',
            'values': [
                {'value': 'TEST_MONGO_1', 'priority': 1}
            ]
        },
        'gradingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Grading Provider Implementation',
            'description': 'Implementation for grading provider',
            'values': [
                {'value': 'TEST_MONGO_1', 'priority': 1}
            ]
        },
        'loggingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Logging Provider Implementation',
            'description': 'Implementation for logging provider',
            'values': [
                {'value': 'TEST_MONGO_1', 'priority': 1}
            ]
        },
    }
}
'''


TEST_SERVICE = {
    'id': 'dlkit_runtime_bootstrap_configuration',
    'displayName': 'DLKit Runtime Bootstrap Configuration',
    'description': 'Bootstrap Configuration for DLKit Runtime',
    'parameters': {
        'implKey': impl_key_dict('service'),
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
        'assessment_authoringProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Authoring Provider Implementation',
            'description': 'Implementation for assessment authoring service provider',
            'values': [
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
        'authorizationProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Authorization Provider Implementation',
            'description': 'Implementation for authorization service provider',
            'values': [
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
        # 'learningProviderImpl': {
        #     'syntax': 'STRING',
        #     'displayName': 'Learning Provider Implementation',
        #     'description': 'Implementation for learning service provider',
        #     'values': [
        #         {'value': HANDCAR_IMPL, 'priority': 1}
        #     ]
        # },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
        'commentingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Commenting Provider Implementation',
            'description': 'Implementation for commenting service provider',
            'values': [
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
        'resourceProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Resource Provider Implementation',
            'description': 'Implementation for resource service provider',
            'values': [
                {'value': 'TEST_RESOURCE_AGENT_AUTHZ_ADAPTER_1', 'priority': 1}
            ]
        },
        'gradingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Grading Provider Implementation',
            'description': 'Implementation for grading provider',
            'values': [
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
        'loggingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Logging Provider Implementation',
            'description': 'Implementation for logging provider',
            'values': [
                {'value': 'GSTUDIO_1', 'priority': 1}
            ]
        },
    }
}