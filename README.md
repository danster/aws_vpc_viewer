aws_vpc_viewer - a toolkit for checking the vpc framework on AWS conveniently.
===================================
Danster Huang (c) 2014-2014  
huangmaofeng@126.com

These scripts (shell or python) is run on the EC2 instance of AWS.  

Platform:  

- Ubuntu 64bit 14.04 LTS
- MacOS 10.9.5

Dependencies:  

- python 2.7
- python package : json, pyparsing, pydot, xlsxwriter
- pyparsing: load DOT files.
- Graphviz: render the graphs.
- inkscape: a vector graphics editor, transforms svg file to png file. 
- AWS Command Line Interface

If you want to analysis my code, some following knowledge are required :

- [Dot Language](http://www.graphviz.org/doc/info/lang.html)
- [Node, Edge and Graph Attributes](http://www.graphviz.org/doc/info/attrs.html)
- [pydot](https://code.google.com/p/pydot/)
- [XlsxWriter](https://xlsxwriter.readthedocs.org/)
- [AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-set-up.html#cli-signup)
- [Amazon VPC](http://aws.amazon.com/documentation/vpc/)


Running
-----------------------------------
   
    $ git clone https://danster@github.com:/danster/aws_vpc_viewer.git vpcgraph
    $ cd /path/to/vpcgraph/
    $ python json2dot.py --help 

