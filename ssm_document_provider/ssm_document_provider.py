import json
import boto3
import logging
import cfnresponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')


def handler(event, context):
    kwargs = event['ResourceProperties'].copy()

    if 'ServiceToken' in kwargs:
        del kwargs['ServiceToken']

    if kwargs.get( 'DocumentFormat', 'JSON') and isinstance(kwargs.get('Content'), dict):
        kwargs['Content'] = json.dumps(kwargs['Content'])

    try:
        if event['RequestType'] == 'Create':
            response = ssm.create_document(**kwargs)
        elif event['RequestType'] == 'Update':
            kwargs.pop('DocumentType')
            kwargs['DocumentVersion'] = '$LATEST'
            response = ssm.update_document(**kwargs)
        elif event['RequestType'] == 'Delete':
            response = ssm.delete_document(Name=kwargs.get('Name'))

        return cfnresponse.send(event, context, cfnresponse.SUCCESS, response.get('DocumentInformation', {}), kwargs.get('Name'))
    except Exception as e:
        logger.error('%s', e)
        if event.get('RequestType') != 'Delete':
            return cfnresponse.send(event, context, cfnresponse.FAILED, {}, kwargs.get('Name'))
        else:
            return cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, kwargs.get('Name'))

