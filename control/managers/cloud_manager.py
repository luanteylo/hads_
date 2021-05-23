# Each supported cloud have to implemented the follows methods


class CloudManager:
    # VM STATE
    PENDING = 'pending'
    RUNNING = 'running'
    STOPPING = 'stopping'
    STOPPED = 'stopped'
    SHUTTING_DOWN = 'shutting-down'
    TERMINATED = 'terminated'
    HIBERNATING = 'hibernating'
    HIBERNATED = 'stop - hibernate'

    ERROR = 'error'
    ABORT = 'abort'

    # QUEUE STATE
    IDLE = 'idle'
    WORKING = 'working'  # == Busy
    FAILED = 'failed'    # == Failed

    # MARKET
    ON_DEMAND = 'on-demand'
    PREEMPTIBLE = 'preemptible'

    BURSTABLE = 'burstable'

    # PROVIDERs
    EC2 = 'ec2'
    GCLOUD = 'gcloud'

    # FILE SYSTEM

    S3 = 's3'
    EBS = 'ebs'
    EFS = 'efs'

    # [START CREATE_INSTANCE]

    # Create an on-demand instance
    # InputConfig: Instance type (str)
    # Return: instance_id (str) or None if instance was not created
    def create_on_demand_instance(self, instance_type):
        pass

    # Create a preemptible_instance
    # InputConfig: Instance type (str)
    # Return: instance_id (str) or None if instance was not created
    def create_preemptible_instance(self, instance_type, max_price):
        pass

    # Create a storage volume (AWS ONLY)
    # InputConfig: Volume size (int), Zone (str)
    # Return: volume id (str) or None if volume was not created
    def create_volume(self, size, zone):
        pass

    # Attach a volume to an instance (AWS ONLY)
    # InputConfig: instance_id (str), volume_id (str), device (str)
    # Return: True if the volume was attached with success or False otherwise
    def attach_volume(self, instance_id, volume_id, device):
        pass

    # Delete a storage volume (AWS ONLY)
    # InputConfig: Volume id (str)
    # Return: True if volume was delete or false otherwise
    def delete_volume(self, volume_id):
        pass

    # [TERMINATE_INSTANCE]

    # Terminate an instance
    # InputConfig: Instance_id (str)
    # Output: Operate State (Success: True, Error: False)
    def terminate_instance(self, instance_id):
        pass

    # [GET_INFO]

    # Return the current status of the VM
    # InputConfig: Instance_id (str)
    # Output: instance_status (str) in lower case or None if Instance not found
    def get_instance_status(self, instance_id):
        pass

    # Return all instances_id
    # InputConfig: Filter (dict)
    # Output: instances_id (List)
    def list_instances_id(self, filter=None):
        '''
                  # Filter Format #

                      search_filter = {
                          'status' :  [ list of VALID STATES]
                      }
                  Valid State:  PENDING, RUNNING, STOPPING, STOPPED
                                SHUTTING_DOWN, TERMINATED, HIBERNATED
           '''
        pass

    # Return the current IP of the VM
    # InputConfig: instance_id
    # Output: ip(str) or None if there is no IP associated to the VM
    def get_instance_ip(self, instance_id):
        pass

    # Return the current CPU credit of a burstable instance
    # InputConfig: Instance_id(str)
    # Ouput: cpu_credits (int) or None if the instance is not burstable
    def get_cpu_credits(self, instance_id):
        pass
