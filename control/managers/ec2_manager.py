from control.managers.cloud_manager import CloudManager

from control.config.ec2_config import EC2Config

import boto3

from datetime import datetime
from dateutil.tz import tzutc
from datetime import timedelta

import logging
import json

import math

from pkg_resources import resource_filename

from ratelimit import limits, sleep_and_retry


class EC2Manager(CloudManager):

    def __init__(self):

        self.ec2_conf = EC2Config()

        self.client = boto3.client('ec2')
        self.resource = boto3.resource('ec2')
        self.cloud_watch = boto3.client('cloudwatch')
        self.session = boto3.Session()
        self.credentials = self.session.get_credentials()

        self.instances_history = {}

    def _new_filter(self, name, values):
        return {
            'Name': name,
            'Values': [v for v in values]
        }

    def _update_history(self, instances, status):
        for i in instances:

            if status == 'start':
                try:
                    i.load()
                except:
                    pass

                self.instances_history = {
                    i.id: {
                        'StartTime': i.launch_time,
                        'EndTime': None,
                        'Instance': i,
                        'Zone': i.placement['AvailabilityZone']
                    }
                }

            if status == 'terminate':
                if i.id in self.instances_history:
                    self.instances_history[i.id]['EndTime'] = \
                        datetime.now(tz=tzutc())

    def _create_instance(self, info, burstable):

        try:

            if burstable:

                instances = self.resource.create_instances(
                    ImageId=info['ImageId'],
                    InstanceType=info['InstanceType'],
                    KeyName=info['KeyName'],
                    MaxCount=info['MaxCount'],
                    MinCount=info['MinCount'],
                    SecurityGroups=info['SecurityGroups'],
                    InstanceMarketOptions=info['InstanceMarketOptions'],
                    TagSpecifications=[
                        {
                            'ResourceType': 'instance',
                            'Tags': [
                                {
                                    'Key': self.ec2_conf.tag_key,
                                    'Value': self.ec2_conf.tag_value
                                }
                            ]
                        }
                    ],
                    Placement=info['Placement'],
                    CreditSpecification={
                        'CpuCredits': 'standard'
                    }
                )

            else:
                instances = self.resource.create_instances(
                    ImageId=info['ImageId'],
                    InstanceType=info['InstanceType'],
                    KeyName=info['KeyName'],
                    MaxCount=info['MaxCount'],
                    MinCount=info['MinCount'],
                    SecurityGroups=info['SecurityGroups'],
                    InstanceMarketOptions=info['InstanceMarketOptions'],
                    TagSpecifications=[
                        {
                            'ResourceType': 'instance',
                            'Tags': [
                                {
                                    'Key': self.ec2_conf.tag_key,
                                    'Value': self.ec2_conf.tag_value
                                }
                            ]
                        }
                    ],
                    Placement=info['Placement']
                )

            self._update_history(instances, 'start')

            for i in instances:
                i.wait_until_running()

            return instances

        except Exception as e:
            logging.error("<EC2Manager>: Error to create instance")
            logging.error(e)
            return None

    def create_volume(self, size, zone):

        try:
            ebs_vol = self.client.create_volume(
                Size=size,
                AvailabilityZone=zone,
                TagSpecifications=[
                    {
                        'ResourceType': 'volume',
                        'Tags': [
                            {
                                'Key': self.ec2_conf.tag_key,
                                'Value': self.ec2_conf.tag_value
                            },
                        ]
                    },
                ],
            )

            if ebs_vol['ResponseMetadata']['HTTPStatusCode'] == 200:

                return ebs_vol['VolumeId']
            else:
                return None

        except Exception as e:

            logging.error("<EC2Manager>: Error to create Volume")
            logging.error(e)
            return None

    def wait_volume(self, volume_id):
        waiter = self.client.get_waiter('volume_available')
        waiter.wait(
            VolumeIds=[
                volume_id
            ]
        )

    def attach_volume(self, instance_id, volume_id, device):

        try:
            self.client.attach_volume(
                VolumeId=volume_id,
                InstanceId=instance_id,
                Device=device
            )
            return True
        except Exception as e:
            logging.error("<EC2Manager>: Error to attach volume {} to instance {}".format(volume_id,
                                                                                          instance_id))
            logging.error(e)
            return False

    def create_on_demand_instance(self, instance_type, burstable=False):

        parameters = {

            'ImageId': self.ec2_conf.image_id,
            'InstanceType': instance_type,
            'KeyName': self.ec2_conf.key_name,
            'MaxCount': 1,
            'MinCount': 1,
            'SecurityGroups': [
                self.ec2_conf.security_group,
                self.ec2_conf.security_vpc_group
            ],
            'InstanceMarketOptions': {},
            'Placement': {'AvailabilityZone': self.ec2_conf.zone},
        }

        instances = self._create_instance(parameters, burstable)

        if instances is not None:
            created_instances = [i for i in instances]
            instance = created_instances[0]
            return instance.id
        else:
            return None

    def delete_volume(self, volume_id):
        try:
            self.client.delete_volume(VolumeId=volume_id)
            status = True
        except Exception as e:
            logging.error("<EC2Manager>: Error to delete Volume {} ".format(volume_id))
            logging.error(e)
            status = False

        return status

    def create_preemptible_instance(self, instance_type, max_price, burstable=False):

        # user_data = '''#!/bin/bash
        # /usr/bin/enable-ec2-spot-hibernation
        # echo "user-data" > $HOME/control-applications/test_user_data.txt
        # '''

        zone = self.ec2_conf.zone
        interruption_behaviour = 'hibernate'

        parameters = {
            'ImageId': self.ec2_conf.image_id,
            'InstanceType': instance_type,
            'KeyName': self.ec2_conf.key_name,
            'MaxCount': 1,
            'MinCount': 1,
            'SecurityGroups': [
                self.ec2_conf.security_group,
                self.ec2_conf.security_vpc_group
            ],
            'InstanceMarketOptions':
                {
                    'MarketType': 'spot',
                    'SpotOptions': {
                        'MaxPrice': str(max_price),
                        'SpotInstanceType': 'persistent',
                        'InstanceInterruptionBehavior': interruption_behaviour
                    }
                },
            'Placement': {}
            # 'UserData': user_data
        }

        if zone:
            parameters['Placement'] = {'AvailabilityZone': zone}

        instances = self._create_instance(parameters, burstable)

        if instances is not None:
            created_instances = [i for i in instances]
            instance = created_instances[0]
            return instance.id
        else:
            return None

    def _terminate_instance(self, instance):

        # if instance is spot, we have to remove its request
        if instance.instance_lifecycle == 'spot':
            self.client.cancel_spot_instance_requests(
                SpotInstanceRequestIds=[
                    instance.spot_instance_request_id
                ]
            )

        self._update_history([instance], status='terminate')

        instance.terminate()

    def terminate_instance(self, instance_id, wait=True):

        try:

            instance = self.__get_instance(instance_id)

            self._terminate_instance(instance)

            if wait:
                instance.wait_until_terminated()

            status = True

        except Exception as e:
            logging.error("<EC2Manager>: Error to terminate instance {}".format(instance_id))
            logging.error(e)

            status = False

        return status

    @sleep_and_retry
    @limits(calls=10, period=1)
    def __get_instance(self, instance_id):

        try:

            instance = self.resource.Instance(instance_id)

            instance.reload()
        except Exception as e:
            logging.info(e)
            return None

        return instance

    def __get_instances(self, search_filter=None):

        if search_filter is None:
            return self.resource.instances.filter()

        _filters = []

        if 'status' in search_filter:
            _filters.append(
                self._new_filter(
                    name="instance-state-name",
                    values=search_filter['status']
                )
            )

        # if 'lifecycle' in filters:
        #     _filters.append(
        #         self._new_filter(
        #             name="instance-lifecycle",
        #             values=filters['lifecycle']
        #         )
        #     )
        # if 'request_id' in filters:
        #     _filters.append(
        #         self._new_filter(
        #             name="spot-instance-request-id",
        #             values=filters['request_id']
        #         )
        #     )
        #
        # if 'tag' in filters:
        #     _filters.append(
        #         self._new_filter(
        #             name='tag:{}'.format(filters['tag']['name']),
        #             values=filters['tag']['values']
        #         )
        #     )

        return [i for i in self.resource.instances.filter(Filters=_filters)]

    def get_instance_status(self, instance_id):

        if instance_id is None:
            return None

        instance = self.__get_instance(instance_id)

        if instance is None:
            return None
        else:
            return instance.state["Name"].lower()

    def list_instances_id(self, search_filter=None):
        instances = self.__get_instances(search_filter)

        return [i.id for i in instances]

    def get_instance_ip(self, instance_id):
        instance = self.__get_instance(instance_id)

        if instance is None:
            return None
        else:
            return instance.public_ip_address

    @staticmethod
    def get_preemptible_price(instance_type, zone=None):

        _filters = [
            {
                'Name': 'product-description',
                'Values': ['Linux/UNIX']
            }
        ]

        if zone is not None:
            _filters.append(
                {
                    'Name': 'availability-zone',
                    'Values': [zone]
                }
            )

        client = boto3.client('ec2')

        history = client.describe_spot_price_history(
            InstanceTypes=[instance_type],
            Filters=_filters,
            StartTime=datetime.now()
        )

        return [(h['AvailabilityZone'], float(h['SpotPrice'])) for h in history['SpotPriceHistory']]

    # Get current AWS price for an on-demand instance
    @staticmethod
    def get_ondemand_price(instance_type, region):
        # Search product search_filter
        FLT = '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},' \
              '{{"Field": "operatingSystem", "Value": "Linux", "Type": "TERM_MATCH"}},' \
              '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},' \
              '{{"Field": "instanceType", "Value": "{t}", "Type": "TERM_MATCH"}},' \
              '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
              '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'

        # translate region code to region name
        endpoint_file = resource_filename('botocore', 'data/endpoints.json')

        with open(endpoint_file, 'r') as f:
            data = json.load(f)
        region = data['partitions'][0]['regions'][region]['description']

        f = FLT.format(r=region, t=instance_type)
        # Get price info
        pricing = boto3.client('pricing')
        data = pricing.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
        od = json.loads(data['PriceList'][0])['terms']['OnDemand']
        id1 = list(od)[0]
        id2 = list(od[id1]['priceDimensions'])[0]

        return float(od[id1]['priceDimensions'][id2]['pricePerUnit']['USD'])

    def get_cpu_credits(self, instance_id):

        end_time = datetime.utcnow()

        start_time = end_time - timedelta(minutes=5)

        # print(start_time)
        # print(end_time)

        response = self.cloud_watch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUCreditBalance',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            Period=60,
            Statistics=['Average'],
            StartTime=start_time,
            EndTime=end_time
        )

        cpu_credits = 0

        if len(response['Datapoints']) > 0:
            cpu_credits = math.ceil(response['Datapoints'][-1]['Average'])

        return cpu_credits
