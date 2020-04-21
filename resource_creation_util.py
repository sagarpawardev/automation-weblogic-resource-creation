"""
#################################################################

# Author : Sagar Pawar (sagar.pawar@oracle.com)

This script helps in creating following resources:
    - Manage Server
    - File Store
    - JMS Server
    - Subdeployment
    - Queue Connection Factories
    - XA Queues
    - Queues
    - System Module

*** IMPORTANT ***:- Currently Script Does not Support Datasource Creation. You have to create it Manually

Note:- If Resources Already exists then script skips the resource and move to next resource

Pending Improvements:-
    Setting SSL ports
    Datasource creation
#################################################################
"""

import sys

# Reading Properties
fpath_prop = 'property/project.properties'
l = list()
for line in open(fpath_prop):
    if "=" in line and not line.startswith("#"):
        l.append(line.strip().split('='))

props = dict(l)

# Flags
want_to_create_mangserver = True
if props['create_mangserver'] == "N": want_to_create_mangserver = False
print "Want to create MangServer: " + str(want_to_create_mangserver)

want_to_create_xa_qcf = True
if props['create_xa_qcf'] == "N": want_to_create_xa_qcf = False

want_to_create_filestore = True
if props['create_filestore'] == "N": want_to_create_filestore = False

want_to_create_jmserver = True
if props['create_jmserver'] == "N": want_to_create_jmserver = False

want_to_create_subdeployment = True
if props['create_subdeployment'] == "N": want_to_create_subdeployment = False

want_to_create_qcf = True
if props['create_qcf'] == "N": want_to_create_qcf = False

want_to_create_queues = True
if props['create_queues'] == "N": want_to_create_queues = False

want_to_create_systemmodule = True
if props['create_systemmodule'] == "N": want_to_create_systemmodule = False

want_to_append_module_name = True
if props['append_env_name'] == "N": want_to_append_module_name = False


# Variables
manage_server = props['manage_server']
system_module = props['system_module']
jms_server = props['jms_server']
subdeployment = props['subdeployment']
filestore = props['filestore']

# File Paths
fpath_queues = props['queues_filepath']
fpath_qcfs_xa = props['qcfxa_filepath']
fpath_qcfs = props['qcf_filepath']

# Module
module_name = props['env']
print "Module -->", module_name

# Server Credentials
weblogic_uname = props['weblogic_uname']
weblogic_pass = props['weblogic_pass']
protocol = props['protocol']
weblogic_url = protocol + '://' + props['weblogic_url']
file_store_dir = props['filestore_dir']
print "Username --> " + weblogic_uname
print "Password --> " + weblogic_pass
print "URL --> " + weblogic_url
print "File Store Directory --> " + file_store_dir
print

# Queues
f_queues = open(fpath_queues, 'r')
queues = [queue.strip() for queue in f_queues]
f_queues.close()
print '==> Found', len(queues), 'queues in', fpath_queues

# XA Queue Connection Factories
f_qcf_xa = open(fpath_qcfs_xa, 'r')
queue_conn_fact_xa = [qcf_xa.strip() for qcf_xa in f_qcf_xa]
f_qcf_xa.close()
print '==> Found', len(queue_conn_fact_xa), 'XA QCF in', fpath_qcfs_xa

# Queue Connection Factories
f_qcf = open(fpath_qcfs, 'r')
queue_conn_fact = [qcf.strip() for qcf in f_qcf]
f_qcf.close()
print '==> Found', len(queue_conn_fact), 'Queue Connection Factories in', fpath_qcfs
# sys.exit(0)

# Initializing Variables
'''Assigning Default Values'''
print '==> Assigning Default Values if Not found'
if manage_server is None:
    manage_server = "MangServer_" + module_name
print '==> Manage Server Name is: ', manage_server

if system_module is None:
    system_module = "SystemModule_" + module_name
print '==> System Module Name is: ', system_module

if jms_server is None:
    jms_server = "JMSServer_" + module_name
print '==> JMS Server Name is: ', jms_server

if subdeployment is None:
    subdeployment = "FCUBS_" + module_name
print '==> Subdeployment Name is: ', subdeployment

if filestore is None:
    filestore = "FileStore_" + module_name
print '==> Filestore Name is: ', filestore

############## DO NOT TOUCH #############
import weblogic.descriptor.BeanAlreadyExistsException


try:
    print 'Trying to connect with App Server...'
    connect(weblogic_uname, weblogic_pass, weblogic_url)
except:
    print '**Not able to connect with App Server using user:'+weblogic_uname
    print '**Try Following:'
    print '1. Check port it should be same as that of weblogic console URL port (probably 7001,)'
    print '2. If you are using hostname (like localhost) try using IP directly(like 10.184.153.139)'
    print '3. If still not working ask admin to give all permissions to your user in Weblogic Oracle_Home'
    sys.exit(1)

try:
    '''Initialization'''
    print '------------Initializing------------'
    edit()
    startEdit()
except:
    print '**Invalid Port Please use Weblogic Console port NOT managed server port'
    sys.exit(1)
    


def next_available_port():
    print '==> Entering next_available_port()'
    # Suppress ls() Output
    if os.name == 'nt':
        redirect('/dev/null', 'false')
    servers = ls('/Servers', returnMap='true')
    print servers
    ports = list()
    for server in servers:
        print '==> Goint to Dir: ' + '/Servers/' + server
        cd('/Servers/' + server)
        port = cmo.getListenPort()
        ports.append(port)
    ports.sort()
    curr_port = ports[0]
    for port in ports:
        if port > curr_port:
            break
        else:
            curr_port = curr_port + 1
    # Activate ls Output
    stopRedirect()
    print '==> Exiting next_available_port() Return: ' + str(curr_port)
    return curr_port


def create_dir(directory):
    print '==> Creating FileStore Directory: '+directory
    if not os.path.exists(directory):
        os.makedirs(directory)
        print '==> FileStore Directory "' + directory + '" Created...'
    else:
        print '==> FileStore Directory "' + directory + '" Already Exisits'


def systemmodule_exists():
    try:
        system_module_path = '/JMSSystemResources/' + system_module
        cd(system_module_path)
        cd('/')
        return True
    except:
        # Create System Module
        return False


def filestore_exists():
    try:
        filestore_path = '/FileStores/' + filestore
        cd(filestore_path)
        cd('/')
        return True
    except:
        # Create System Module
        return False


def mangserver_exists():
    try:
        mang_server_path = '/Servers/' + manage_server
        cd(mang_server_path)
        cd('/')
        return True
    except:
        # Create System Module
        return False


def jmsserver_exists():
    try:
        jms_server_path = '/JMSServers/' + jms_server
        cd(jms_server_path)
        cd('/')
        return True
    except:
        # Create System Module
        return False


def subdeployment_exists():
    if not systemmodule_exists(): return False
    try:
        subdeployment_path = '/JMSSystemResources/' + system_module + '/SubDeployments/' + subdeployment
        cd(subdeployment_path)
        cd('/')
        return True
    except:
        # Create System Module
        return False


def create_mangserver():
    '''Creating Manage Server'''
    print '------------Creating Manage Server------------'

	
    # Check Manager Server Existence
    try:
        mang_server_path = '/Servers/' + manage_server
        cd(mang_server_path)
        print '==> Manage Server "' + manage_server + '" already exists'
    except:
        print '==> Creating Manage Server "' + manage_server + '"...'
        # Create Manage Server
        cd('/')
        cmo.createServer(manage_server)
        cd(mang_server_path)
        cmo.setListenAddress('')
        port = next_available_port()
        print 'Setting Port "'+str(port)+'" For Your Manager Server'
        cmo.setListenPort(port)
        # Enable SSL port
        cmo.setCluster(None)
        mang_server_ssl_path = mang_server_path + '/SSL/' + manage_server
        cd(mang_server_ssl_path)
        cmo.setEnabled(true)
        cmo.setListenPort(1000 + port)
        print '==> Manage Server Created: ', manage_server


def create_filestore():
    '''Creating FileStore'''
    print '------------Creating File Store------------'

    if not mangserver_exists():
        print '==>** Manage Server "' + manage_server + '" Does not exist!!'
        print '==>** Create this and Retry'
        return

    # Check FileStore Existence
    try:
        filestore_path = '/FileStores/' + filestore
        cd(filestore_path)
        print '==> Filestore "' + filestore + '" already exists'
    except:
        print '==> Filestore "' + filestore + '"...'
        # Create File Store
        cd('/')
        cmo.createFileStore(filestore)
        cd(filestore_path)
        create_dir(file_store_dir)  # Need to check permissions Here
        cmo.setDirectory(file_store_dir + filestore)
        set('Targets', jarray.array([ObjectName('com.bea:Name=' + manage_server + ',Type=Server')], ObjectName))
        print '==> File Store Created: ', filestore


def create_jmsserver():
    '''Creating JMS Server'''
    print '------------Creating JMS Server------------'	

    if not mangserver_exists():
        print '==>** Manage Server "' + manage_server + '" Does not exist!!'
        print '==>** Create it and Retry'
        return
    if not filestore_exists():
        print '==>** File Store "' + filestore + '" Does not exist!!'
        print '==>** Create it and Retry'
        return

    # Check JMS Server Existence
    try:
        jms_server_path = '/JMSServers/' + jms_server
        cd(jms_server_path)
        print '==> JMS Server "' + jms_server + '" already exists'
    except:
        print '==> Creating JMS Server "' + jms_server + '"...'
        # Create JMS Server
        cd('/')
        cmo.createJMSServer(jms_server)
        cd('/JMSServers/' + jms_server)
        cmo.setPersistentStore(getMBean('/FileStores/' + filestore))
        set('Targets', jarray.array([ObjectName('com.bea:Name=' + manage_server + ',Type=Server')], ObjectName))
        print '==> JMS Server Created: ', jms_server


def create_systemmodule():
    '''Creating System Module'''
    print '------------Creating System Module------------'
    if not mangserver_exists():
        print '==>** Manage Server "' + manage_server + '" Does not exist!!'
        print '==>** Create it and Retry'
        return

    # Check System Module Existence
    try:
        system_module_path = '/JMSSystemResources/' + system_module
        cd(system_module_path)
        print '==> System Module "' + system_module + '" already exists'
    except:
        print '==> Creating System Module "' + system_module + '"...'
        # Create System Module
        cd('/')
        cmo.createJMSSystemResource(system_module)
        cd('/JMSSystemResources/' + system_module)
        set('Targets', jarray.array([ObjectName('com.bea:Name=' + manage_server + ',Type=Server')], ObjectName))
        print '==> System Module Created: ', system_module


def create_subdeployment():
    '''Creating Subdeployment'''
    print '------------Creating Subdeployment------------'
    if not systemmodule_exists():
        print '==>** System Module "' + system_module + '" Does not exist!!'
        print '==>** Create it and Retry'
        return
    if not jmsserver_exists():
        print '==>** JMS Server "' + jms_server + '" Does not exist!!'
        print '==>** Create it and Retry'
        return

    # Check SubDeployment Existence
    try:
        subdeployment_path = '/JMSSystemResources/' + system_module + '/SubDeployments/' + subdeployment
        cd(subdeployment_path)
        print '==> Subdeployment "' + subdeployment + '" already exists'
    except:
        print '==> Creating SubDeployment "' + subdeployment + ' in Module "' + system_module + '"...'
        # Create SubDeployment
        cd('/')
        cd('/JMSSystemResources/' + system_module)
        cmo.createSubDeployment(subdeployment)
        cd('/JMSSystemResources/' + system_module + '/SubDeployments/' + subdeployment)
        set('Targets', jarray.array([ObjectName('com.bea:Name=' + jms_server + ',Type=JMSServer')], ObjectName))
        print '==> SubDeployment Created:', subdeployment


def create_qcf():
    '''Creating Queue Connection Factories'''
    print '------------Creating Queue Connection Factories------------'
    print '==> Found' + str(len(queue_conn_fact)) + 'Queue Connection Factories in' + fpath_qcfs

    if not systemmodule_exists():
        print '==>** System Module "' + system_module + '" Does not exist!!'
        print '==>** Create it and Retry'
        return

    for i in range(len(queue_conn_fact)):
        qcf_jndi = queue_conn_fact[i]
        qcf_name = qcf_jndi
		
        #If empty then ignore
        qcf_name = qcf_name.strip()
        if not qcf_name:
            print 'This QCF Name is empty so ignoring :D'
            continue
		
        if want_to_append_module_name:
            qcf_name = qcf_jndi + "_" + module_name

        # Check QCF existence
        qcf_xa_path = '/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_name
        try:
            cd(qcf_xa_path)
            print '==> Queue Connection Factory "' + qcf_name + '" already exists with JNDI Name ' + qcf_jndi
            continue
        except:
            print '==> Creating Queue Connection Factory ' + qcf_name + ' with JNDI "' + qcf_jndi + '"...'
            pass

        # Creating XA Queue Connection Factories
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module)
        cmo.createConnectionFactory(qcf_name)
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_name)
        cmo.setJNDIName(qcf_jndi)
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_name + '/SecurityParams/' + qcf_name)
        cmo.setAttachJMSXUserId(false)
        cmo.setSecurityPolicy('ThreadBased')
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_name + '/ClientParams/' + qcf_name)
        cmo.setClientIdPolicy('Restricted')
        cmo.setSubscriptionSharingPolicy('Exclusive')
        cmo.setMessagesMaximum(10)
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_name + '/TransactionParams/' + qcf_name)
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_name)
        cmo.setDefaultTargetingEnabled(true)
        print '==> Queue Connection Factory Created: ', qcf_name + " with JNDI " + qcf_jndi


def create_queues():
    '''Creating Queues'''
    print '------------Creating Queues------------'
    print '==> Found', str(len(queues)), 'queues in', fpath_queues

    if not systemmodule_exists():
        print '==>** System Module "' + system_module + '" Does not exist!!'
        print '==>** Create it and Retry'
        return
    if not subdeployment_exists():
        print '==>** Subdeployment "' + subdeployment + '" Does not exist!!'
        print '==>** Create it and Retry'
        return
    if not jmsserver_exists():
        print '==>** JMS Server "' + jms_server + '" Does not exist!!'
        print '==>** Create it and Retry'
        return

    for i in range(len(queues)):
        queue_jndi = queues[i]
        queue_name = queue_jndi
		
        #If Empty then ignore
        queue_name = queue_name.strip()
        if not queue_name:
            print 'This Queue Name is empty so ignoring :D'
            continue
		
		
        if want_to_append_module_name:
            queue_name = queue_jndi + "_" + module_name

        # Check queue existence
        queue_path = '/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/Queues/' + queue_name
        try:
            cd(queue_path)
            print '==> Queue "' + queue_jndi + '" with name "'+queue_name+'" already exists'
            continue
        except:
            print '==> Creating Queue ' + queue_jndi + ' with name "'+queue_name+'...'
            pass

        # Creating Queue
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '')
        cmo.createQueue(queue_name)
        cd(queue_path)
        cmo.setJNDIName(queue_jndi)
        cmo.setSubDeploymentName(subdeployment)
        cd('/JMSSystemResources/' + system_module + '/SubDeployments/' + subdeployment)
        set('Targets', jarray.array([ObjectName('com.bea:Name=' + jms_server + ',Type=JMSServer')], ObjectName))
        print '==> Queue Created: ', queue_jndi


def create_xa_qcf():
    '''Creating XA Queue Connection Factories'''
    print '------------Creating XA Queue Connection Factories------------'
    print '==> Found', len(queue_conn_fact_xa), 'XA QCF in', fpath_qcfs_xa
	
    if not systemmodule_exists():
        print '==>** System Module "' + system_module + '" Does not exist!!'
        print '==>** Create it and Retry'
        return

    for i in range(len(queue_conn_fact_xa)):
        qcf_xa_jndi = queue_conn_fact_xa[i]
        qcf_xa_name = qcf_xa_jndi
		
        #If empty then ignore
        qcf_xa_name = qcf_xa_name.strip()
        if not qcf_xa_name:
            print 'This XA QCF Name is empty so ignoring :D'
            continue
        
        if want_to_append_module_name:
            qcf_xa_name = qcf_xa_jndi + "_" + module_name

        # Check QCF_XA existence
        qcf_xa_path = '/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_xa_name
        try:
            cd(qcf_xa_path)
            print '==> XA Queue Connection Factory "' + qcf_xa_name + '" already exists with JNDI Name '+qcf_xa_jndi
            continue
        except:
            print '==> Creating XA Queue Connection Factory ' + qcf_xa_name + ' with JNDI "'+ qcf_xa_jndi +'"...'
            pass

        # Creating XA Queue Connection Factories
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module)
        cmo.createConnectionFactory(qcf_xa_name)
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_xa_name)
        cmo.setJNDIName(qcf_xa_jndi)
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_xa_name + '/SecurityParams/' + qcf_xa_name)
        cmo.setAttachJMSXUserId(false)
        cmo.setSecurityPolicy('ThreadBased')
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_xa_name + '/ClientParams/' + qcf_xa_name)
        cmo.setClientIdPolicy('Restricted')
        cmo.setSubscriptionSharingPolicy('Exclusive')
        cmo.setMessagesMaximum(10)
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_xa_name + '/TransactionParams/' + qcf_xa_name)
        cmo.setXAConnectionFactoryEnabled(true)
        cd('/JMSSystemResources/' + system_module + '/JMSResource/' + system_module + '/ConnectionFactories/' + qcf_xa_name)
        cmo.setDefaultTargetingEnabled(true)
        print '==> XA Queue Connection Factory Created: ', qcf_xa_name+" with JNDI "+qcf_xa_jndi


# -------- EXECUTION -----------------
if want_to_create_mangserver:
    create_mangserver()
else:
    print "==> Skipped Manage Server Creation"

if want_to_create_filestore:
    create_filestore()
else:
    print "==> Skipped File Store Creation"

if want_to_create_jmserver:
    create_jmsserver()
else:
    print "==> Skipped JMS Server Creation"

if want_to_create_systemmodule:
    create_systemmodule()
else:
    print "==> Skipped System Module Creation"

if want_to_create_subdeployment:
    create_subdeployment()
else:
    print "==> Skipped Subdeployment Creation"

if want_to_create_qcf:
    create_qcf()
else:
    print "==> Skipped Queue Connection Factory(QCF) Creation"

if want_to_create_queues:
    create_queues()
else:
    print "==> Skipped Queue Creation"

if want_to_create_xa_qcf:
    create_xa_qcf()
else:
    print "==> Skipped XA Queue Connection Factory Creation"

'''Activate'''
activate()
