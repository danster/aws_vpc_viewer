aws_vpc_viewer - a toolkit for checking the vpc framework on AWS conveniently.
===================================
Danster Huang (c) 2014-2014
huangmaofeng@126.com

these scripts (shell or python) is run on the EC2 instance of AWS.

------------------------------------

Platform:  
- Ubuntu 64bit 14.04 LTS or MacOS 10.9

Dependencies:  
- python 2.7
- python package : json, pydot, xlsxwriter
- pyparsing: load DOT files.
- Graphviz: render the graphs.
- inkscape: a vector graphics editor, transforms svg file to png file. 
- AWS Command Line Interface

if you want to analysis my code, some following knowledge are required :
- [Dot Language](http://www.graphviz.org/doc/info/lang.html)
- [Node, Edge and Graph Attributes](http://www.graphviz.org/doc/info/attrs.html)
- [pydot](https://code.google.com/p/pydot/)
- [XlsxWriter](https://xlsxwriter.readthedocs.org/)
- [AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-set-up.html#cli-signup)
- [Amazon VPC](http://aws.amazon.com/documentation/vpc/)

-----------------------------------

Running
------

```
$ cd /path/to/aws_vpc_viewer/  
$ /bin/bash painter.sh # draws the network topology of your vpc on AWS into png photoes.
```
