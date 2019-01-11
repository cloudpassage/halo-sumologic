import boto3
from botocore.exceptions import ClientError


class ManageState(object):
    """All state (timestamp) management happens in this class.

    Args:
        aws_region (str): AWS region.
        ssm_param_name (str): Name for SSM parameter.
        ssm_param_desc (str): Description string for SSM param.
    """
    def __init__(self, aws_region, ssm_param_name, ssm_param_desc):
        self.client = boto3.client('ssm', region_name=aws_region)
        self.param_name = ssm_param_name
        self.param_desc = ssm_param_desc

    def get_timestamp(self):
        """Get the timestamp currrently stored in the SSM parameter."""
        param = self.client.get_parameter(Name=self.param_name)
        timestamp = param['Parameter']['Value']
        return timestamp

    def set_timestamp(self, timestamp):
        """Delete and re-create SSM parameter."""
        try:
            # We do this so that we won't exceed the max param versions
            self.client.delete_parameter(Name=self.param_name)
        except ClientError as e:
            msg = "Exception when attempting to remove timestamp from SSM: {}"
            print(msg.format(e))
        response = self.client.put_parameter(Name=self.param_name,
                                             Description=self.param_desc,
                                             Value=timestamp, Type='String',
                                             Overwrite=True)
        msg = 'Updated timestamp parameter named {} with {} (version {})'
        print(msg.format(self.param_name, timestamp, response['Version']))
        return

    def increment_timestamp(self, timestamp):
        """Only update SSM parameter ()faster than delete/re-create."""
        response = self.client.put_parameter(Name=self.param_name,
                                             Description=self.param_desc,
                                             Value=timestamp, Type='String',
                                             Overwrite=True)
        msg = 'Updated timestamp parameter named {} with {} (version {})'
        print(msg.format(self.param_name, timestamp, response['Version']))
        return
