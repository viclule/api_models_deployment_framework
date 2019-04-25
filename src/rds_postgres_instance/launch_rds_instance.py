import boto3


rds_client = boto3.client('rds', region_name='eu-central-1')

RDS_DB_SUBNET_GROUP = 'rds-db_subnet_group'


def create_db_subnet_group():
    print('Creating RDS DB Subnet Group ' + RDS_DB_SUBNET_GROUP)
    rds_client.