#!/usr/bin/python
# -*- coding: utf-8 -*-

#
#   Exporting resource lists to Excel
#   Author: Huangmaofeng
#   Date: 2014-10-28

import json
import os
import glob
import sys
import copy
import xlsxwriter
from collections import Counter

VERSION = '1.0'

VALID_PROJECTS = (
    (1, 'tmap-beluga'),
    (2, 'tmap-cassowary'),
    (3, 'tmap-bobofeel'),
    (4, 'demo-fitch'),
    (5, 'iauto-demo')
)
VOLUME_MAPs = {'standard': 'Magnetic',
               'gp2': 'General Purpose(SSD)',
               'io1': 'Provisioned IOPS(SSD)'}

data, workbook = {}, {}
for item in VALID_PROJECTS:
    proj = item[1]
    data[proj] = list()
    workbook[proj] = xlsxwriter.Workbook(proj+"_Inventory.xlsx")

BASE_DIR = os.path.split(os.path.realpath(__file__))[0]


def fileCheck(file):
    try:
        f = open(file)
        return f
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        sys.exit()
    else:
        print "Unexpected error:", sys.exc_info()[0]
        f.close()
        sys.exit()


def _get_vol_from_ec2(instanceID):
    vol_jsons = glob.glob(os.path.join(BASE_DIR, "ec2")+os.sep+"vol*")

    volumes = []
    for vf in vol_jsons:
        _vol_file = fileCheck(vf)
        vol_desc = json.load(_vol_file)

        for volume in vol_desc['Volumes']:
            if instanceID == volume['Attachments'][0]['InstanceId']:
                volumes.append("%sG %s" % (volume['Size'],
                                           VOLUME_MAPs[volume['VolumeType']]))

        _vol_file.close()

    vols_ct = Counter(volumes)
    EBS = " / ".join([t+" x"+str(n) for t, n in vols_ct.items()])

    return EBS


def _dataSource_ec2():
    result = copy.deepcopy(data)
    ec2_jsons = glob.glob(os.path.join(BASE_DIR, "ec2")+os.sep+"ec2*")

    for f in ec2_jsons:
        _ec2_file = fileCheck(f)
        ec2_desc = json.load(_ec2_file)

        for reservation in ec2_desc['Reservations']:
            instance = reservation['Instances'][0]

            if 'Tags' not in instance:
                continue

            proj = None

            for tag in instance['Tags']:
                if tag['Key'] == 'project':
                    proj = tag['Value']
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']

            if proj in [item[1] for item in VALID_PROJECTS]:
                try:
                    IamRoleArn = instance['IamInstanceProfile']['Arn']
                    IamRole = IamRoleArn.split("/")[-1]
                except KeyError:
                    IamRole = None

                if instance['PublicDnsName']:
                    PublicIpAddress = instance['NetworkInterfaces'][0]['Association']['PublicIp']
                else:
                    PublicIpAddress = None

                EBS = _get_vol_from_ec2(instance['InstanceId'])

                result[proj].append([
                    instance['Placement']['AvailabilityZone'],
                    instance['InstanceId'],
                    instance_name,
                    instance['InstanceType'],
                    instance['ImageId'],
                    instance['State']['Name'],
                    instance['PublicDnsName'],
                    PublicIpAddress,
                    instance['NetworkInterfaces'][0]['PrivateDnsName'],
                    instance['NetworkInterfaces'][0]['PrivateIpAddress'],
                    instance['VpcId'],
                    instance['SubnetId'],
                    IamRole,
                    EBS])

        _ec2_file.close()

    return result


def generate_worksheet_ec2(workbook, data_source):
    ec2_worksheet = workbook.add_worksheet("EC2")

    data_nums = len(data_source)

    if data_nums > 0:
        # Set the columns widths.
        for idx in range(len(data_source[0])):
            ec2_worksheet.set_column(1+idx, 1+idx, _max_len(data_source, idx))

        # Add a table to the worksheet.
        ec2_worksheet.add_table('B3:O'+str(data_nums+3), {
            'data': data_source, 'columns': [{'header': 'Available Zone'},
                                             {'header': 'Instance ID'},
                                             {'header': 'Name'},
                                             {'header': 'Instance Type'},
                                             {'header': 'AMI ID'},
                                             {'header': 'State'},
                                             {'header': 'Public DNS'},
                                             {'header': 'Public IP'},
                                             {'header': 'Private DNS'},
                                             {'header': 'Private IP'},
                                             {'header': 'VPC ID'},
                                             {'header': 'Subnet ID'},
                                             {'header': 'Role'},
                                             {'header': 'EBS'}]
            })


def _get_tags_from_elb(LoadBalancerName):
    elb_tags = glob.glob(os.path.join(BASE_DIR, "elb")+os.sep+"tags*")

    for t in elb_tags:
        _elb_tags = fileCheck(t)
        tags_desc = json.load(_elb_tags)

        for tgdesc in tags_desc['TagDescriptions']:
            if LoadBalancerName == tgdesc['LoadBalancerName']:
                return tgdesc['Tags']

        _elb_tags.close()
    return


def _dataSource_elb():
    result = copy.deepcopy(data)
    elb_jsons = glob.glob(os.path.join(BASE_DIR, "elb")+os.sep+"elb*")

    for f in elb_jsons:
        _elb_file = fileCheck(f)
        elb_desc = json.load(_elb_file)

        for elb in elb_desc['LoadBalancerDescriptions']:
            tags = _get_tags_from_elb(elb['LoadBalancerName'])

            proj = None
            for tag in tags:
                if tag and tag['Key'] == 'project':
                    proj = tag['Value']

            if proj and proj in [item[1] for item in VALID_PROJECTS]:
                result[proj].append([
                    elb['LoadBalancerName'],
                    "/".join(elb['AvailabilityZones']),
                    elb['DNSName'],
                    elb['VPCId'],
                    "/".join(elb['Subnets']),
                    "/".join(elb['SecurityGroups']),
                    "/".join([i['InstanceId'] for i in elb['Instances']])
                    ])

        _elb_file.close()

    return result


def generate_worksheet_elb(workbook, data_source):
    elb_worksheet = workbook.add_worksheet("ELB")

    data_nums = len(data_source)

    if data_nums > 0:
        # Set the columns widths.
        for idx in range(len(data_source[0])):
            elb_worksheet.set_column(1+idx, 1+idx, _max_len(data_source, idx))

        # Add a table to the worksheet.
        elb_worksheet.add_table('B3:H'+str(data_nums+3), {
            'data': data_source, 'columns': [{'header': 'Name'},
                                             {'header': 'Available Zone'},
                                             {'header': 'DNS Name'},
                                             {'header': 'VPC ID'},
                                             {'header': 'Subnet ID'},
                                             {'header': 'SecurityGroups'},
                                             {'header': 'Instances'}]
            })


def _get_tags_from_rds(Region, DBInstanceIdentifier):
    file_name = "tags_"+Region+"_"+DBInstanceIdentifier+".json"
    tag_file = os.path.join(BASE_DIR, "rds")+os.sep+file_name
    _rds_tags = fileCheck(tag_file)
    tags_desc = json.load(_rds_tags)

    _rds_tags.close()

    return tags_desc['TagList']


def _dataSource_rds():
    result = copy.deepcopy(data)
    rds_jsons = glob.glob(os.path.join(BASE_DIR, "rds")+os.sep+"rds*")

    for f in rds_jsons:
        _rds_file = fileCheck(f)
        rds_desc = json.load(_rds_file)

        for rds in rds_desc['DBInstances']:
            tags = _get_tags_from_rds(rds['AvailabilityZone'][:-1],
                                      rds['DBInstanceIdentifier'])

            proj = None
            for tag in tags:
                if tag and tag['Key'] == 'project':
                    proj = tag['Value']

            if proj and proj in [item[1] for item in VALID_PROJECTS]:
                Endpoint = rds['Endpoint']['Address'] + ":" + \
                    str(rds['Endpoint']['Port'])
                Storage = "%sG %s" % (rds['AllocatedStorage'],
                                      VOLUME_MAPs[rds['StorageType']])

                result[proj].append([
                    rds['DBInstanceIdentifier'],
                    rds['AvailabilityZone'][:-1],
                    rds['AvailabilityZone'],
                    rds['Engine'],
                    Endpoint,
                    rds['DBSubnetGroup']['VpcId'],
                    rds['DBInstanceClass'],
                    Storage,
                    rds['DBInstanceStatus'],
                    rds['MultiAZ'],
                    rds['MasterUsername'],
                    ])

        _rds_file.close()

    return result


def generate_worksheet_rds(workbook, data_source):
    rds_worksheet = workbook.add_worksheet("RDS")

    data_nums = len(data_source)

    if data_nums > 0:
        # Set the columns widths.
        for idx in range(len(data_source[0])):
            rds_worksheet.set_column(1+idx, 1+idx, _max_len(data_source, idx))

        # Add a table to the worksheet.
        rds_worksheet.add_table('B3:L'+str(data_nums+3), {
            'data': data_source, 'columns': [{'header': 'DB Identifier'},
                                             {'header': 'Region'},
                                             {'header': 'Available Zone'},
                                             {'header': 'Engine'},
                                             {'header': 'Endpoint'},
                                             {'header': 'VPC ID'},
                                             {'header': 'DBInstance Class'},
                                             {'header': 'Storage'},
                                             {'header': 'Status'},
                                             {'header': 'MultiAZ'},
                                             {'header': 'User'}]
            })


def _get_logging_from_bucket(bucket):
    file_name = "log_"+bucket+".json"
    log_file = os.path.join(BASE_DIR, "s3")+os.sep+file_name
    _s3_log = fileCheck(log_file)

    try:
        log_desc = json.load(_s3_log)
    except ValueError:
        _s3_log.close()
        return None

    _s3_log.close()

    return log_desc['LoggingEnabled']['TargetPrefix'] + \
        log_desc['LoggingEnabled']['TargetBucket']


def _get_version_from_bucket(bucket):
    file_name = "ver_"+bucket+".json"
    ver_file = os.path.join(BASE_DIR, "s3")+os.sep+file_name
    _s3_ver = fileCheck(ver_file)
    contents = _s3_ver.read()

    _s3_ver.close()

    return contents


def _get_loc_from_bucket(bucket):
    file_name = "loc_"+bucket+".json"
    loc_file = os.path.join(BASE_DIR, "s3")+os.sep+file_name
    _s3_loc = fileCheck(loc_file)
    loc_desc = json.load(_s3_loc)

    _s3_loc.close()

    return loc_desc['LocationConstraint']


def _get_tags_from_bucket(bucket):
    file_name = "tags_"+bucket+".json"
    tag_file = os.path.join(BASE_DIR, "s3")+os.sep+file_name
    _s3_tags = fileCheck(tag_file)

    try:
        tags_desc = json.load(_s3_tags)
    except ValueError:
        _s3_tags.close()
        return []

    _s3_tags.close()
    return tags_desc['TagSet']


def _dataSource_s3():
    result = copy.deepcopy(data)

    _s3_file = fileCheck(os.path.join(BASE_DIR, "s3")+os.sep+"buckets.json")
    s3_desc = json.load(_s3_file)

    for bkt in s3_desc['Buckets']:
        tags = _get_tags_from_bucket(bkt['Name'])

        proj = None
        for tag in tags:
            if tag and tag['Key'] == 'project':
                proj = tag['Value']

        if proj and proj in [item[1] for item in VALID_PROJECTS]:
            Region = _get_loc_from_bucket(bkt['Name'])
            Versiong = _get_version_from_bucket(bkt['Name'])
            Logging = _get_logging_from_bucket(bkt['Name'])

            result[proj].append([bkt['Name'],
                                 Region,
                                 bkt['CreationDate'],
                                 Versiong,
                                 Logging
                                 ])

    return result


def generate_worksheet_s3(workbook, data_source):
    s3_worksheet = workbook.add_worksheet("S3")

    data_nums = len(data_source)

    if data_nums > 0:
        # Set the columns widths.
        for idx in range(len(data_source[0])):
            s3_worksheet.set_column(1+idx, 1+idx, _max_len(data_source, idx))

        # Add a table to the worksheet.
        s3_worksheet.add_table('B3:F'+str(data_nums+3), {
            'data': data_source, 'columns': [{'header': 'Bucket Name'},
                                             {'header': 'Region'},
                                             {'header': 'Creation Date'},
                                             {'header': 'Versioning'},
                                             {'header': 'Logging'}
                                             ]
            })


def _max_len(data, i):
    tmp = list()
    for d in data:
	try:
            tmp.append(len(d[i]))
        except TypeError:
            tmp.append(0)

    return max(tmp)

# main
ec2_data = _dataSource_ec2()
elb_data = _dataSource_elb()
rds_data = _dataSource_rds()
s3_data = _dataSource_s3()

for item in VALID_PROJECTS:
    proj = item[1]
    generate_worksheet_ec2(workbook[proj], ec2_data[proj])
    generate_worksheet_elb(workbook[proj], elb_data[proj])
    generate_worksheet_rds(workbook[proj], rds_data[proj])
    generate_worksheet_s3(workbook[proj], s3_data[proj])

    # To ensure files closed
    workbook[proj].close()

