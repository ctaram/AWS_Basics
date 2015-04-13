from boto.vpc import VPCConnection
import time
from boto import ec2
from boto.ec2 import address
def get_user_data():
	        user_data = """#!/bin/bash
		       		sudo apt-get -y update
			        sudo apt-get install default-jdk
			        sudo apt-get install -y tomcat7
			        sudo service tomcat7 start"""
		return user_data

def create_ec2_instance(ec2_conn,ami_id,key_name,user_data,security_group,subnet_id,network_interface):

	        ec2_instance = ec2_conn.run_instances(ami_id,key_name=key_name,instance_type='t2.small',user_data=user_data,security_group_ids=[security_group],subnet_id=subnet_id,network_interfaces=network_interface)
		image = ec2_instance.instances[0]
		while image.state != 'running':
			print image.state
			time.sleep(30)
			image.update()
		return ec2_instance

def create_security_group(ec2_conn,vpc_id,security_group_name):
	        groups = ec2_conn.get_all_security_groups()
		for group in groups :
			if group.name == security_group_name :
				return group
		web = ec2_conn.create_security_group(security_group_name,vpc_id=vpc_id,description='ABC Talks Group')
		web.authorize('tcp',8080,8080,'0.0.0.0/0')
		return web
def create_network_interface(ec2_conn,domain='vpc',public=False,subnet=None,groups=None,description=None):
	elastic_network_interface = ec2_conn.create_network_interface(subnet,groups=groups,description=description)
	if public:
		elastic_ip_address = ec2_conn.allocate_address(domain=domain)
		associated_address = ec2_conn.associate_address(allocation_id=elastic_ip_address.allocation_id,network_interface_id=elastic_network_interface.id)
	return elastic_netowrk_interface 
vpc_connection = VPCConnection(aws_access_key_id='',aws_secret_access_key='')
vpc = vpc_connection.create_vpc('10.0.0.0/16')
print vpc.id
print vpc.state
time.sleep(60)
print vpc.state
subnet = vpc_connection.create_subnet(vpc.id,'10.0.0.0/25')
print subnet.state
print subnet.available_ip_address_count
ec2_conn = ec2.connect_to_region('us-east-1',aws_access_key_id='AKIAIORQIQAOE42JZKWQ',aws_secret_access_key='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')

web = create_security_group(ec2_conn,vpc.id,'abctalks1')
#address = address.Address(connection=ec2_conn,instance_id=ec2_instance.instances[0].id)
print address
network_interface = create_network_interface(ec2_conn,public=True,subnet=subnet,groups=[web.id],description='Storm Cluster')
ec2_instance = create_ec2_instance(ec2_conn,'ami-d05e75b8','abctalks',get_user_data(),web.id,subnet.id,network_interface)
