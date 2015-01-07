#!/usr/bin/python
# -*- coding: utf-8 -*-

#   Generating dot documents from json file
#   Author: Huangmaofeng
#   Date: 2014-11-27

import copy
import getopt
import os
import pydot
import sys
import string

from json2dict import getInstances, getNetworks
from utils import usage

VERSION = '1.0'
OUTFILE = ''
BASE_DIR = os.path.split(os.path.realpath(__file__))[0]
ICONS_DIR = os.path.join(BASE_DIR, "icons")
GRAPH_DIR = os.path.join(BASE_DIR, "graph")

REGIONS = ['ap-southeast-1','ap-northeast-1']
aws = ''

def fileCheck(_file):
    try:
        f = open(_file)
        return f
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        sys.exit()

                
def getVpcMap():

    global aws
    instances = getInstances()
    subnets, vpcs, zones = getNetworks()

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
 

def getInstancesTree():
    global aws
    instances = getInstances()
    subnets, vpcs, zones = getNetworks()
    
    DotAttrs = dict(color='black', fontsize='12',
                    overlap='false', sep='+1,1', 
                    rankdir='TB', ranksep='3 equality', 
                    clusterrank='local', compound='true')
    
    NodeAttrs = dict(shape='none', width='2', height='2', labelloc='b',
                     fontsize='18', imagescale='true', 
                     style='rounded')
    
    EdgeAttrs = dict(dir='none', color='black')
    
    print 'generating dot data ... '
    aws = pydot.Dot('AWS', graph_type='digraph', label='', **DotAttrs)
    root = pydot.Node('AWS', label='', image=ICONS_DIR+os.sep+"Cloud AWS.png", **NodeAttrs)
    aws.add_node(root)

    for i in instances :               
        instance_id = string.replace(i['InstanceId'], '-', '_')
        label =  'EC2  '+instance_id+'\n'
        if 'PrivateIpAddress' in i :
            label += 'Private IP '+i['PrivateIpAddress']+'\n'
        if 'PublicIpAddress' in i :
            label += 'Public IP '+i['PublicIpAddress']+'\n'
           
        _Attrs = copy.deepcopy(NodeAttrs)
        _Attrs.update(dict(height='3.2',))    
        instance = pydot.Node(instance_id, label=label,image=ICONS_DIR+os.sep+"EC2 Instance.png", 
                              **_Attrs)
        i['Node'] = instance
        aws.add_node(instance)
    
    isolated_instances = [it for it in instances if 'VpcId' not in it ]
    instances = [it for it in instances if 'VpcId' in it ]

    for r in REGIONS :
        _region = string.replace(r, '-', '_')
        label='Region \n'+_region
        _Attrs = copy.deepcopy(NodeAttrs)
        _Attrs.update(dict(height='2.2',)) 
        region = pydot.Node(label, label=label, image=ICONS_DIR+os.sep+"Clound Internet.png", 
                            **_Attrs)
        
        aws.add_node(region)
        aws.add_edge(pydot.Edge(root, region, **EdgeAttrs))
        
        for z in zones :
            if z['Region'] != r : continue
            zone_name = string.replace(z['ZoneName'], '-', '_')
            label='AvailablityZone \n'+zone_name
            
            _Attrs = copy.deepcopy(NodeAttrs)
            _Attrs.update(dict(height='1', shape='box', labelloc='c'))
            zone = pydot.Node(label, label=label, **_Attrs)

            aws.add_node(zone)
            aws.add_edge(pydot.Edge(region, zone, **EdgeAttrs))
            
            for i in isolated_instances :
                if i['Placement']['AvailabilityZone'] == z['ZoneName'] :
                    aws.add_edge(pydot.Edge(zone, i['Node'], dir='none', color='black'))
                    
        
        for v in vpcs :
            if v['Region'] != r : continue
            
            vpc_id = string.replace(v['VpcId'], '-', '_')
            label = 'Default ' if v['IsDefault'] is True else ''
            label += ' '+vpc_id+'\n'+ v['CidrBlock']
            _Attrs = copy.deepcopy(NodeAttrs)
            _Attrs.update(dict(height='2.5',)) 
            vpc = pydot.Node(label, label=label, image=ICONS_DIR+os.sep+"Cloud VPC.png", 
                             **NodeAttrs)
            
            aws.add_node(vpc)
            aws.add_edge(pydot.Edge(region, vpc, **EdgeAttrs))
 
            for s in subnets :
                if s['VpcId'] != v['VpcId'] : continue
                subnet_id = string.replace(s['SubnetId'], '-', '_')
                label = subnet_id+'\n'+s['CidrBlock']+'\n'
                
                _Attrs = copy.deepcopy(NodeAttrs)
                _Attrs.update(dict(height='1', shape='box', labelloc='c'))
                subnet = pydot.Node(label, label=label, **_Attrs)
                aws.add_node(subnet)
                aws.add_edge(pydot.Edge(vpc, subnet, **EdgeAttrs))
                 
                for i in instances :
                    if i['SubnetId'] != s['SubnetId'] : continue
                    aws.add_edge(pydot.Edge(subnet, i['Node'], **EdgeAttrs))


def funcFork():
    
    global OUTFILE
    opts = list()
    isMap = True
    
    try: 
        opts, _args = getopt.getopt(sys.argv[1:], 'htmi:o:v',['version','outfile='])
    except getopt.GetoptError:  
        usage()
    
    for op, value in opts :
        if op in ('-h', '--help'):
            usage()
            sys.exit()
        elif op in ('-v', '--version'):
            print 'AWS VPC Viewer Version: ' + VERSION
            sys.exit()
        elif op in ('-o', '--outfile'):  
            OUTFILE = value
        elif op in ('-t', '--tree'):
            isMap = False
        elif op in ('-m', '--map'):
            isMap = True

    if isMap is True :
        getVpcMap()
    else :
        getInstancesTree()

    print 'drawing a png refer to the dot data ... '
    if OUTFILE == '' :
        aws.write_png("graph/VpcTopologyMap.png")
    else :
        aws.write_png(OUTFILE)


if __name__ == '__main__':
    funcFork()

