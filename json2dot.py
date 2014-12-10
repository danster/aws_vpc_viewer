#!/usr/bin/python
# -*- coding: utf-8 -*-

#   Generating dot documents from json file
#   Author: Huangmaofeng
#   Date: 2014-11-27

from collections import Counter
import copy
import glob
import json
import os
import pydot
import sys
import string


VERSION = '1.0'
BASE_DIR = os.path.split(os.path.realpath(__file__))[0]
VPC_DIR = os.path.join(BASE_DIR, "vpc")
JSON_DIR = os.path.join(BASE_DIR, "json")
ICONS_DIR = os.path.join(BASE_DIR, "icons")
REGIONS = ['ap-southeast-1','ap-northeast-1']

instances = list()
subnets = list()
vpcs = list()
zones = list()

def fileCheck(_file):
    try:
        f = open(_file)
        return f
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        sys.exit()
    else:
        print "Unexpected error:", sys.exc_info()[0]
        f.close()
        sys.exit()

def getInstances():
    print 'generating instance list data ... '
    for region in REGIONS :
        _jsons = glob.glob(VPC_DIR+os.sep+"instances*"+region+"*")
        for js in _jsons:
            _file = fileCheck(js)
            _dict = json.load(_file)
            for info in _dict["Reservations"] :
                for instance in info["Instances"]:
                    it = copy.deepcopy(instance)
                    it['ReservationId'] = info['ReservationId']
                    it['Region'] = region
                    instances.append(it)
            _file.close()

    print 'dumping instance to json file ... '
    with open(JSON_DIR+os.sep+'instances','w') as _file:
        json.dump(instances, _file, indent = 4, separators=(',', ': '))
    print 'dumping instance to json file end. '
    
def getNetworks():
    print 'generating subnets, vpcs and zones data ... '
    for region in REGIONS :
        _jsons = glob.glob(VPC_DIR+os.sep+"subnets*"+region+"*")
        for js in _jsons:
            _file = fileCheck(js)
            _dict = json.load(_file)
            for subnet in _dict["Subnets"] :
                subnet['Region'] = region
                subnets.append(copy.deepcopy(subnet))
            _file.close()
            
        _jsons = glob.glob(VPC_DIR+os.sep+"vpcs*"+region+"*")
        for js in _jsons:
            _file = fileCheck(js)
            _dict = json.load( fileCheck(js) )
            for vpc in _dict["Vpcs"] :
                vpc['Region'] = region
                vpcs.append(copy.deepcopy(vpc))
            _file.close()
        
        _jsons = glob.glob(VPC_DIR+os.sep+"availablity_zones*"+region+"*")
        for js in _jsons:
            _file = fileCheck(js)
            _dict = json.load( fileCheck(js) )
            for zone in _dict["AvailabilityZones"] :
                zone['Region'] = region
                zones.append(copy.deepcopy(zone))
            _file.close()
    
    print 'dumping datum of subnets, vpcs, zones to json file ... '
    with open(JSON_DIR+os.sep+'subnets','w') as _file:
        json.dump(subnets, _file, indent = 4, separators=(',', ': '))
    with open(JSON_DIR+os.sep+'vpcs','w') as _file:
        json.dump(vpcs, _file, indent = 4, separators=(',', ': '))
    with open(JSON_DIR+os.sep+'zones','w') as _file:
        json.dump(zones, _file, indent = 4, separators=(',', ': '))
    print 'dumping is end. '
    
            
def getDot():
    
    global REGIONS, instances, subnets, vpcs
    print 'generating dot data ... '
    # color: surround color, bgcolor: background color, fontcolor
    aws = pydot.Dot('AWS', graph_type='digraph', label='AWS',
                    color='black', style='rounded', clusterrank='local', 
                    fontsize='12', ranksep ='2 equality',compound='true', rankdir='TB',
                    remincross='false', area='100',  model='circuit')
    
    aws_flage = pydot.Node('AWS', label='', shape='none',
                           image=ICONS_DIR+os.sep+"Cloud AWS.png")
    aws.add_node(aws_flage)

    for i in instances :               
        instance_id = string.replace(i['InstanceId'], '-', '_')
        label =  'EC2  '+instance_id+'\n'
        if 'PrivateIpAddress' in i :
            label += 'Private IP '+i['PrivateIpAddress']+'\n'
        if 'PublicIpAddress' in i :
            label += 'Public IP '+i['PublicIpAddress']+'\n'
        instance = pydot.Node(instance_id, label=label, shape='none',
                 labelloc='b', overlap='false', fontsize='10',
                 image=ICONS_DIR+os.sep+"EC2 Instance.png")
        aws.add_node(instance)
        i['Node'] = instance
    
    isolated_instances = [it for it in instances if 'VpcId' not in it ]
    instances = [it for it in instances if 'VpcId' in it ]

    region_flags = list()
    
    for r in REGIONS :
        _region = string.replace(r, '-', '_')
        label='Region '+_region
        region = pydot.Subgraph('cluster_'+_region, graph_type='digraph',
                        label='', labelloc='b',)
        aws.add_subgraph(region)
        
        region_flage = pydot.Node(label, label=label, shape='none',
                  labelloc='b', overlap='false', fontsize='20',
                  image=ICONS_DIR+os.sep+"Clound Internet.png")
        region.add_node(region_flage)
        region_flags.append(region_flage)
        

        for z in zones :
            if z['Region'] != r : continue
            zone_name = string.replace(z['ZoneName'], '-', '_')
            zone = pydot.Subgraph('cluster_'+zone_name, graph_type='digraph', 
                    label='Zone '+zone_name)
            region.add_subgraph(zone) 
            
            [ region.add_node(i['Node']) for i in isolated_instances              
                    if i['Placement']['AvailabilityZone'] == z['ZoneName'] ]
                    
        vpc_flags = list()
        
        for v in vpcs :
            if v['Region'] != r : continue
            vpc_id = string.replace(v['VpcId'], '-', '_')
            label = 'Default VPC' if v['IsDefault'] is True else 'VPC'
            label += '\n'+ v['CidrBlock']
            vpc = pydot.Subgraph('cluster_'+vpc_id, graph_type='digraph',
                                label='')
            region.add_subgraph(vpc) 
            
            vpc_flage = pydot.Node(label, label=label, shape='box', color='transparent',
                  labelloc='b', overlap='false', fontsize='18')
                  # image=ICONS_DIR+os.sep+"Cloud VPC.png"
            vpc.add_node(vpc_flage)
            vpc_flags.append(vpc_flage)
            
            subnet_flags = list()
 
            for s in subnets :
                if s['VpcId'] != v['VpcId'] : continue
                subnet_id = string.replace(s['SubnetId'], '-', '_')
                
                subnet = pydot.Subgraph('cluster_'+subnet_id, graph_type='digraph')
                vpc.add_subgraph(subnet)
                
                subnet_flag = pydot.Node(subnet_id+'\n'+s['CidrBlock']+'\n', shape='plaintext',
                    labelloc='b', overlap='false', fontsize='20')
                subnet.add_node(subnet_flag)
                subnet_flags.append(subnet_flag)
                 
                for i in instances :
                    if i['SubnetId'] != s['SubnetId'] : continue
                    subnet.add_node(i['Node'])
                    
                for i in range(0, len(subnet_flags)-1):
                    vpc.add_edge(pydot.Edge(subnet_flags[i], subnet_flags[i+1],
                            dir='none', color='transparent'))   
        for i in range(0, len(vpc_flags)-1):
            region.add_edge(pydot.Edge(vpc_flags[i], vpc_flags[i+1],
                     dir='none', color='transparent'))
         
    for i in range(0, len(region_flags)-1):
        aws.add_edge(pydot.Edge(region_flags[i], region_flags[i+1],
                dir='none', color='transparent'))
                                                 
    print 'writing the dot data to a file ... '
    with open(BASE_DIR+'/AWS_VPC.dot','w') as _file:
        _file.write(aws.to_string())
        
    print 'drawing a png refer to the dot data ... '
    aws.write_png("AWS_VPC.png")
    print 'drawing is completed. '
    

if __name__ == '__main__':
    getInstances()
    getNetworks()
    getDot()

