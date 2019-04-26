import boto3
from botocore.exceptions import ClientError


rds_client = boto3.client('rds', region_name='eu-central-1')


RDS_DB_SUBNET_GROUP = 'rds-db_subnet_group'
SECURITY_GROUP_NAME = 'rds_public_security_group'

def create_db_subnet_group():
    """Create a DB Subnet Group"""
    print('Creating RDS DB Subnet Group ' + RDS_DB_SUBNET_GROUP)
    rds_client.create_db_subnet_group(
        DBSubnetGroupName=RDS_DB_SUBNET_GROUP,
        DBSubnetGroupDescription='A DB subnet group.',
        SubnetIds=['subnet-04260549', 'subnet-098cafe6796ca685e',
                   'subnet-3eef0e54', 'subnet-4b9fc336']
    )

def create_db_security_group_and_add_inbound_rule():
    """Create a DB Security Group and add inbound rules"""
    ec2 = boto3.client('ec2', region_name='eu-central-1')

    # create security group
    security_group = ec2.create_security_group(
        GroupName=SECURITY_GROUP_NAME,
        Description='rds security group to allow public access',
        VpcId='vpc-f4dae49f'
    )

    # get id of the security group
    security_group_id = security_group['GroupId']
    print('Created RDS security group with id ' + security_group_id)

    # add public access rule to security group
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
            'FromPort': 5432,
            'ToPort': 5432,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
    print('Added inbound access rule to security group id ' + security_group_id)
    return security_group_id

def retrive_security_group_id_if_already_existant():
    """Retrieve the Security Group ID if the Group already exists"""
    print('Retrieving security group if for ' + SECURITY_GROUP_NAME)
    ec2 = boto3.client('ec2', region_name='eu-central-1')
    res = ec2.describe_security_groups(GroupNames=[SECURITY_GROUP_NAME,])
    security_group_id = res['SecurityGroups'][0]['GroupId']
    return security_group_id


def launch_rds_instance():
    """Launch an RDS Postgres Instance"""
    print("Launching AWS RDS PostgreSQL instance...")

    try:
        security_group_id = create_db_security_group_and_add_inbound_rule()
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.Duplicate':
            security_group_id = retrive_security_group_id_if_already_existant()

    try:
       create_db_subnet_group()
       print("Created DB Subnet Group")
    except ClientError as e:
        if e.response['Error']['Code'] == 'DBSubnetGroupAlreadyExists':
            security_group_id = retrive_security_group_id_if_already_existant()
        print(RDS_DB_SUBNET_GROUP + ' already exists.')

    rds_client.create_db_instance(
        DBName='PostgreSQLDBInstance_API_Models_Framework',
        DBInstanceIdentifier="postgresqlinstanceidentifier",
        DBInstanceClass="db.t2.micro",
        Engine="postgres",
        EngineVersion="10.6",
        Port=5432,
        MasterUsername="postgres",
        MasterUserPassword="mypostgrespassword",
        AllocatedStorage=20,
        MultiAZ=False,
        StorageType="gp2",
        PubliclyAccessible=True,
        VpcSecurityGroupIds=[security_group_id],
        DBSubnetGroupName=RDS_DB_SUBNET_GROUP
    )
    print('An Postgres DB instance was created!')


if __name__ == '__main__':
    launch_rds_instance()