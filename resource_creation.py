'''
#################################################################

# Author : Sagar Pawar

This script helps in creating following resources:
	- Manage Server
	- File Store
	- JMS Server
	- Subdeployment
	- Queue Connection Factories
	- XA Queues
	- Queues
Note:- If Resources Already exists then script skips the resource and move to next resource
	
Steps to un Script:-
    1. Paste File on server
    2. Go in /scratch/oracle/Oracle/Middleware/Oracle_Home/oracle_common/common/bin
    3. Run following command "sh wlst.sh <File Path>" [e.g. sh wlst.sh /scratch/dumps/create_queue.py]
	
Pending Improvements:-
	Setting SSL ports
	Datasource creation
	FileStore storage directory creation
#################################################################
'''

#Module
module_name = 'Script'

#Server Credentials
weblogic_uname = 'weblogic'
weblogic_pass = 'weblogic123'
weblogic_url = 't3://localhost:7001'

#Queues
queues=[
'NOTIFY_DEST_QUEUE',
'DEFFERED_DEST_QUEUE',
'NOTIFY_QUEUE',
'NOTIFY_QUEUE_DLQ',
'EMS_QUEUE_BACK',
'EMS_QUEUE_DLQ',
'EMS_INQUEUE',
'EMS_OUTQUEUE',
'SFMS_INQUEUE',
'RTGS_INQUEUE',
'INTERNAL_BIPREPORT_QUEUE',
'INTERNAL_BIP_QUEUE_DLQ',
'INTERNAL_BIPADVREPORT_QUEUE',
'INTERNAL_BIP_ADVICE_QUEUE_DLQ',
'INTERNAL_GI_UPLOAD_QUEUE',
'INTERNAL_GI_UPLOAD_DLQ',
'ELMDB_REQ_Q',
'ELMDB_RES_Q',
'ELMDB_DLQ',
'EL_NOTIFY_REQ_Q',
'EL_NOTIFY_RES_Q',
'EL_NOTIFY_DLQ',
]

#XA Queue Connection Factories
queue_conn_fact_xa=[
'NotifyDestQCF',
'DefferedDestQCF',
'NOTIFY_MDB_QCF',
'EmsQcf',
'BIPQCF',
'GI_UPLOAD_QCF',
'ELMDBQCF',
'EL_NOTIFY_QCF'
]

#Queue Connection Factories
queue_conn_fact=[
]

#Optional
file_store_dir = '/scratch/work_area/'

#--------------------Script Starts <DO NOT TOUCH>-------------------------
import weblogic.descriptor.BeanAlreadyExistsException

'''----------------UTILS----------------'''
class Util:
	def getNextAvailablePort(self):
		print '==> Entering getNextAvailablePort()'
		#Suppress ls() Output
		redirect('/dev/null','false')
		servers = ls('/Servers',returnMap='true')
		print servers
		ports = list()
		for server in servers:
		    print '==>Goint to Dir: '+'/Servers/'+server
		    cd('/Servers/'+server)
		    port = cmo.getListenPort()
		    ports.append(port)
		ports.sort()
		curr_port = ports[0]
		for port in ports:
		    if port > curr_port:
			    break
		    else:
			    curr_port = curr_port+1
		#Activate ls Output
		stopRedirect()
		print '==> Exiting getNextAvailablePort() Return: '+str(curr_port)
		return curr_port

	def createDirIfNotExists(self, path):
		pass


'''Creating Variables'''
manage_server = "MangServer_" + module_name
system_module = "SystemModule_" + module_name
jms_server = "JMSServer_" + module_name
subdeployment = "FCUBS_" + module_name
filestore = "FileStore_" + module_name

'''Initialization'''
print '------------Initializing------------'
connect(weblogic_uname, weblogic_pass, weblogic_url)
edit()
startEdit()
util = Util()

'''Creating Manage Server'''
print '------------Creating Manage Server------------'
#Check Manager Server Existence
try:
    mang_server_path = '/Servers/' + manage_server
    cd(mang_server_path)
    print '==>Manage Server "' + manage_server + '" already exists'
except:
    print '==>Creating Manage Server "' + manage_server +'"...'
    #Create Manage Server    
    cd('/')
    cmo.createServer(manage_server)
    cd(mang_server_path)
    cmo.setListenAddress('')
	port = util.getNextAvailablePort()
    cmo.setListenPort(port)
	#Enable SSL port
    cmo.setCluster(None)
	mang_server_ssl_path = mang_server_path + '/SSL/' + manage_server
    cd(mang_server_ssl_path)
    cmo.setEnabled(true)
    cmo.setListenPort(1000+port)

'''Creating FileStore'''
print '------------Creating File Store------------'
#Check FileStore Existence
try:
    filestore_path = '/FileStores/'+filestore
    cd(filestore_path)
    print '==>Filestore "' + filestore + '" already exists'
except:
    print '==>Filestore "' + filestore +'"...'
    #Create File Store
    cd('/')
    cmo.createFileStore(filestore)
    cd(filestore_path)
    cmo.setDirectory(file_store_dir + filestore)
    set('Targets',jarray.array([ObjectName('com.bea:Name='+manage_server+',Type=Server')], ObjectName))

'''Creating JMS Server'''
print '------------Creating JMS Server------------'
#Check JMS Server Existence
try:
    jms_server_path = '/JMSServers/' + jms_server
    cd(jms_server_path)
    print '==>JMS Server "' + jms_server + '" already exists'
except:
    print '==>Creating JMS Server "' + jms_server +'"...'
    #Create JMS Server    
    cmo.createJMSServer(jms_server)
    cd('/JMSServers/' + jms_server)
    cmo.setPersistentStore(getMBean('/FileStores/' + filestore))
    set('Targets',jarray.array([ObjectName('com.bea:Name='+manage_server+',Type=Server')], ObjectName))
    
'''Creating Subdeployment'''
print '------------Creating Subdeployment------------'
#Check SubDeployment Existence
try:
    subdeployment_path = '/JMSSystemResources/'+system_module+'/SubDeployments/'+subdeployment
    cd(subdeployment_path)
    print '==>Subdeployment "' + subdeployment + '" already exists'
except:
    print '==>Creating SubDeployment "' + subdeployment +'"...'
    #Create SubDeployment
    cd('/JMSSystemResources/'+system_module)
    cmo.createSubDeployment(subdeployment)
    cd('/JMSSystemResources/'+system_module+'/SubDeployments/'+subdeployment)
    set('Targets',jarray.array([ObjectName('com.bea:Name='+jms_server+',Type=JMSServer')], ObjectName))

'''Creating Queue Connection Factories'''
print '------------Creating Queue Connection Factories------------'
for i in range(len(queue_conn_fact)):
    qcf = queue_conn_fact[i]
    
    #Check QCF_XA existence
    qcf_path = '/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf
    try:
        cd(qcf_path)
        print '==>Queue Connection Factory "' +  qcf + '" already exists'
        continue
    except:
        print '==>Creating Queue Connection Factory ' + qcf +'...'
        pass
        
    #Creating Queue Connection Factories
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module)
    cmo.createConnectionFactory(qcf)
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf)
    cmo.setJNDIName(qcf)
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf + '/SecurityParams/' + qcf)
    cmo.setAttachJMSXUserId(false)
    cmo.setSecurityPolicy('ThreadBased')
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf + '/ClientParams/' + qcf)
    cmo.setClientIdPolicy('Restricted')
    cmo.setSubscriptionSharingPolicy('Exclusive')
    cmo.setMessagesMaximum(10)
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf + '/TransactionParams/' + qcf)
    cmo.setXAConnectionFactoryEnabled(false)
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf)
    cmo.setDefaultTargetingEnabled(true)    

'''Creating Queues'''
print '------------Creating Queues------------'
for i in range(len(queues)):
    queue_name = queues[i]
    
    #Check queue existence
    queue_path = '/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/Queues/'+queue_name
    try:
        cd(queue_path)
        print '==>Queue "' +  queue_name + '" already exists'
        continue
    except:
        print '==>Creating Queue ' + queue_name +'...'
        pass
    
    #Creating Queue
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'')    
    cmo.createQueue(queue_name)
    cd(queue_path)
    cmo.setJNDIName(queue_name)
    cmo.setSubDeploymentName(subdeployment)
    cd('/JMSSystemResources/'+system_module+'/SubDeployments/'+subdeployment)
    set('Targets',jarray.array([ObjectName('com.bea:Name=' + jms_server + ',Type=JMSServer')], ObjectName))

'''Creating XA Queue Connection Factories'''
print '------------Creating XA Queue Connection Factories------------'
for i in range(len(queue_conn_fact_xa)):
    qcf_xa = queue_conn_fact_xa[i]
    
    #Check QCF_XA existence
    qcf_xa_path = '/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf_xa
    try:
        cd(qcf_xa_path)
        print '==>XA Queue Connection Factory "' +  qcf_xa + '" already exists'
        continue
    except:
        print '==>Creating XA Queue Connection Factory ' + qcf_xa +'...'
        pass
        
    #Creating XA Queue Connection Factories
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module)
    cmo.createConnectionFactory(qcf_xa)
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf_xa)
    cmo.setJNDIName(qcf_xa)
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf_xa + '/SecurityParams/' + qcf_xa)
    cmo.setAttachJMSXUserId(false)
    cmo.setSecurityPolicy('ThreadBased')
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf_xa + '/ClientParams/' + qcf_xa)
    cmo.setClientIdPolicy('Restricted')
    cmo.setSubscriptionSharingPolicy('Exclusive')
    cmo.setMessagesMaximum(10)
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf_xa + '/TransactionParams/' + qcf_xa)
    cmo.setXAConnectionFactoryEnabled(true)
    cd('/JMSSystemResources/'+system_module+'/JMSResource/'+system_module+'/ConnectionFactories/' + qcf_xa)
    cmo.setDefaultTargetingEnabled(true)

    
    
'''Activate'''    
activate()
