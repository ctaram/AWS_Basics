from boto import rds
from boto import ec2
from boto.exception import BotoServerError
import sys
import time
from os import path
def get_user_data():
	user_data = """#!/bin/bash
	sudo apt-get -y update
	sudo apt-get install default-jdk
	sudo apt-get install -y tomcat7
	sudo service tomcat7 start"""
	return user_data
def create_rds_instance(rds_conn,instance_id):
	try:
		dbinstance = rds_conn.create_dbinstance(id=instance_id,allocated_storage=5,instance_class='db.t1.micro',master_username='abctalks',master_password='abctalks',port=3306,engine='MySQL5.1',db_name='abctalks')
	except BotoServerError as e:
		if e.error_code == 'DBInstanceAlreadyExists':
			dbinstance = rds_conn.get_all_dbinstances(instance_id=instance_id)[0]

	print dbinstance.status
	while dbinstance.status != 'available' :
		try:
			dbinstance = rds_conn.get_all_dbinstances(instance_id=instance_id)[0]
		except BotoServerError as e:
			if e.error_code == 'DBInstanceNotFound':
			  	print 'try again the instance got deleted'
			  	sys.exit(0)
		print dbinstance.status
		time.sleep(30)
	return dbinstance
def delete_rds_instance(rds_conn,instance_id):
	rds_conn.delete_dbinstance(id=instance_id,skip_final_snapshot=True)

def create_key_pair(ec2_conn,key_pair_name):
	key_pairs = ec2_conn.get_all_key_pairs()
	for key_pair in key_pairs:
		if key_pair.name == key_pair_name :
			return key_pair
	key_pair = ec2_conn.create_key_pair(key_pair_name)
	return key_pair
def create_security_group(ec2_conn,security_group_name):
	groups = ec2_conn.get_all_security_groups()
	for group in groups :
		if group.name == security_group_name :
			return group
	web = ec2_conn.create_security_group(security_group_name,'ABC Talks Group')
	web.authorize('tcp',8080,8080,'0.0.0.0/0')
	web.authorize('ssh',22,22,'0.0.0.0/0')
	return web
def delete_security_group(ec2_conn,security_group_name):
	ec2_conn.delete_secuirty_group(name=security_group_name)
def create_ec2_instance(ec2_conn,ami_id,key_name,user_data,security_group):

	ec2_instance = ec2_conn.run_instances(ami_id,key_name=key_name,instance_type='m1.small',user_data=user_data,security_groups=[security_group])
	image = ec2_instance.instances[0]
	while image.state != 'running':
		print image.state
		time.sleep(30)
		image.update()
	return ec2_instance
def terminate_ec2_instance(ec2_conn,instance_id):
	ec2_conn.terminate_instances(instance_ids=[instance_id])
	
def main():
	rds_conn = rds.RDSConnection(aws_access_key_id='', aws_secret_access_key='')
	ec2_conn = ec2.connect_to_region('us-east-1',aws_access_key_id='',aws_secret_access_key='')
	rds_instance = create_rds_instance(rds_conn,'abctalks')
	security_group = create_security_group(ec2_conn,'abctalks')
	key_pair = create_key_pair(ec2_conn,'abctalks')
	path_to_key = raw_input("Enter the path to store the Key file ("+os.path.dirname(os.path.abspath(__file__))+")")
	if path_to_key != '':
		key_pair.save(path_to_key)
	else:
		key_pair.save(os.path.dirname(os.path.abspath(__file__)))
	ec2_instance = create_ec2_instance(ec2_conn,'ami-4c692a24','abctalks',get_user_data(),'abctalks')
	user_input = raw_input('Do you want to terminate all instances y/N')
	if user_input == 'Y' or user_input == 'y':
		user_input = raw_input('Do you want to terminate RDS instance Y/n')
		if user_input == 'Y' or user_input =='y':
			delete_rds_instance(rds_conn,rds_instance.id)
		user_input = raw_input('Do you want to delete the Security Group Y/n')
		if user_input =='Y' or user_input == 'y':
			delete_security_group(ec2_conn,'abctalks')
		user_input = raw_input('Do you want to delete the Key Pair Y/n')
		if user_input == 'Y' or user_input == 'y':
			terminate_ec2_instance(ec2_conn,ec2_instance.instances[0].id)
if __name__ == "__main__":main()
