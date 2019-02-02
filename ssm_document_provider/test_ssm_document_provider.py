import sys
import json
import boto3
import hashlib
import uuid

from ssm_document_provider import handler

doc = {
    "Name": "SSM-SessionManagerRunShell",
    "DocumentType": "Session",
    "Content": {
        "schemaVersion": "1.0",
        "description": "Document to hold regional settings for Session Manager",
        "sessionType": "Standard_Stream",
        "inputs": {
            "cloudWatchLogGroupName": "ssm-sessions",
            "cloudWatchEncryptionEnabled": True
        }
    }
}

class LambdaContext(object):
    def __init__(self):
        self.function_name: str = ""
        self.function_version: str = ""
        self.invoked_function_arn: str = ""
        self.memory_limit_in_mb: int = 0
        self.aws_request_id: str = ""
        self.log_group_name: str = ""
        self.log_stream_name: str = ""
        self.identity: object = {}
        self.client_context: object = {}

    @staticmethod
    def get_remaining_time_in_millis() -> int:
        return 0

def test_crud():
    try:
        # create 
        request = Request('Create', doc)
        response = handler(request, LambdaContext())
        assert response['Status'] == 'SUCCESS', response['Reason']
        assert response.get('PhysicalResourceId') == doc['Name']

        # update 
        doc['Content']['description'] = 'New document to hold settings'
        request = Request('Update', doc, doc['Name'])
        response = handler(request, LambdaContext())
        assert response['Status'] == 'SUCCESS', response['Reason']
        assert response.get('PhysicalResourceId') == doc['Name']
    finally:
        # delete 
        request = Request('Delete', doc, doc['Name'])
        response = handler(request, LambdaContext())
        assert response['Status'] == 'SUCCESS', response['Reason']

class Request(dict):

    def __init__(self, request_type, properties, physical_resource_id=None):
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': 'request-%s' % uuid.uuid4(),
            'ResourceType': 'Custom::Secret',
            'LogicalResourceId': 'MySecret',
            'ResourceProperties': properties})
        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else str(uuid.uuid4())

if __name__ == '__main__':
    test_crud()
