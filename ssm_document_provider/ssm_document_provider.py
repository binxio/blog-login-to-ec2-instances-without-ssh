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

    logging.info('content => %s', kwargs['Content'])

    try:
        if event['RequestType'] == 'Create':
            response = ssm.create_document(**kwargs)
        elif event['RequestType'] == 'Update':
            kwargs.pop('DocumentType')
            kwargs['DocumentVersion'] = '$LATEST'
            try:
                response = ssm.update_document(**kwargs)
            except ssm.exceptions.DuplicateDocumentContent:
                response = ssm.get_document(Name=kwargs['Name'])
        elif event['RequestType'] == 'Delete':
            response = ssm.delete_document(Name=kwargs.get('Name'))

        return cfnresponse.send(event, context, cfnresponse.SUCCESS, response.get('DocumentInformation', {}), kwargs.get('Name'))
    except Exception as e:
        logger.error('%s', e)
        if event.get('RequestType') != 'Delete':
            return cfnresponse.send(event, context, cfnresponse.FAILED, {}, kwargs.get('Name'))
        else:
            return cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, kwargs.get('Name'))
