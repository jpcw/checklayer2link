

==============================================================
Check *Nix Layer2Link probe Nagios|Icinga|shinken|etc plugin.
==============================================================

.. image:: https://img.shields.io/pypi/l/checklayer2link.svg
    :target: https://pypi.python.org/pypi/checklayer2link/

.. image:: https://img.shields.io/pypi/implementation/checklayer2link.svg
    :target: https://pypi.python.org/pypi/checklayer2link/

.. image:: https://img.shields.io/pypi/pyversions/checklayer2link.svg
    :target: https://pypi.python.org/pypi/checklayer2link/

.. image:: https://img.shields.io/pypi/v/checklayer2link.svg
    :target: https://pypi.python.org/pypi/checklayer2link/

.. image:: https://img.shields.io/pypi/status/checklayer2link.svg
    :target: https://pypi.python.org/pypi/checklayer2link/

.. image:: https://img.shields.io/pypi/wheel/checklayer2link.svg
    :target: https://pypi.python.org/pypi/checklayer2link/

.. image:: https://img.shields.io/coveralls/jpcw/check_layer2link.svg
    :target: https://coveralls.io/r/jpcw/check_layer2link

.. image:: https://api.travis-ci.org/jpcw/check_layer2link.svg?branch=master
    :target: http://travis-ci.org/jpcw/check_layer2link


+ Source: https://github.com/jpcw/checklayer2link

+ Bugtracker: https://github.com/jpcw/checklayer2link/issues

.. contents::

usage
-------

This check runs **ping ip, and ensure ip's mac_address is present in arp_table** then we ensure that layer 2 link is correct, even if a firewall drops icmp.


sample outputs :

+ Ok

::
 
 $ check_layer2link 10.61.0.254
 CHECKLAYER2LINK OK - layer 2 for ip 10.61.0.254 is up | mac=1;;1:1


+ Critical

Critical state is reached with first ignore session not escaped in the optionnal '--ignore-list' 
 
::
 
 $ check_layer2link 10.61.0.254
 CHECKLAYER2LINK CRITICAL - layer 2 for ip 10.61.0.254 is down | mac=0;;1:1


Install
------------

extract the tarball and :: 

    python setup.py install

Maybe you have installed setuptools with ::

    pkg_add py-setuptools

then just ::
    
    easy_install checklayer2link

check_layer2link is located at /usr/local/bin/check_layer2link


Nagios|icinga like configuration
-----------------------------------

check_layer2link could be called localy or remotely via check_by_ssh or NRPE.

**check_by_ssh**

here a sample definition to check remotely by ssh 

Command definition ::
    
    define command{
        command_name    check_ssh_layer2link
        command_line    $USER1$/check_by_ssh -H $ARG1$ -i /var/spool/icinga/.ssh/id_rsa -C "sudo /usr/local/bin/check_layer2link $HOSTADDRESS$"
    }

the service itself ::
    
    define service{
        use                     my-service
        host_name               hostname
        service_description     layer2link
        check_command           check_ssh_layer2link!aa.bb.cc.dd
    }


testing
---------
::
     
     python bootstrap-buildout.py --setuptools-version=33.1.1 --buildout-version=2.5.2
     bin/buildout -N
     bin/test
     
