#Developer - Janarthanan
#Production script
#Make sure to create ".../secret/files" path
#New folder will be created under secret/files as result to store the json

import os,sys,os.path
import time
import requests
import json

#Made change to API port
Cuckoo_Sandbox_API = "http://192.168.2.222:8090"
path_os="secret"


def get_file_info_from_path(dir,topdown=True):
    dirinfo=[]
    for root, dirs, files in os.walk(dir, topdown):
        for name in files:
            dirinfo.append(os.path.join(root,name))
    return dirinfo

def submit_single_sample_debug(filepath):
    REST_URL = Cuckoo_Sandbox_API + "/tasks/create/file"
    SAMPLE_FILE = filepath

    with open(SAMPLE_FILE, "r") as sample:
        files = {"file": (os.path.basename(filepath), sample)}
        r = requests.post(REST_URL, files=files)

    task_id = r.json()["task_id"][0]
    return task_id

def submit_single_sample(file):
    print "Submit File=", file

    r = requests.post(Cuckoo_Sandbox_API + "/tasks/create/submit", files=[
	    ("files", open(file, 'r')),
	])

    #Added by jana
    if(r.status_code==500):
       print "Internal server error has occured!!!!"
       return (-500)
    
    submit_id = r.json()["submit_id"]
    task_ids = 1

    errors = r.json()["errors"]
    return task_ids



def query_task_status():
    r = requests.get(Cuckoo_Sandbox_API + "/tasks/list")
    tasks=r.json()['tasks']
    reports=[]
    for i in tasks:
        reports.append(i['status'])
    return reports

def submit_samples():
    filepath_list = get_file_info_from_path('data')
    i=1
    ids=[]
    for filepath in filepath_list[:]:
        ids.append(submit_single_sample_debug(filepath))
    print(ids)

def get_report_score(id):
    r=requests.get(Cuckoo_Sandbox_API + "/tasks/report/"+str(id))
    if r.status_code!=200:
        print("fail to get report! code:"+str(r.status_code))
        return 0
    score=r.json()['info']['score']
    return score

def delete_task(ids):
    print("delete:")
    for id in ids:
        print("task:"+str(id))
        r=requests.get(Cuckoo_Sandbox_API + "/tasks/delete/"+str(id))
        errors = r.json()
        print(r.json())


def submit_query_report(file):
    # Submit sample
    id= submit_single_sample(file)

    #Added by jana
    #To handle when internal server error occured in Cuckoo while submitting the file
    #Making the file benign
    if(id==-500):	
      return False,-1
 
#    print ("Submission ID= "+ str(id), end= "")
    print "Submission ID= "+ str(id),

    for count in range(10):
        time.sleep(1)
#        print (".", end= "", flush= True)
        print ".",
        sys.stdout.flush()

    print ("\n")


    # Get Status
    report_array= query_task_status()
    report_count= len(report_array)

    print("Report Count= "+ str(report_count))


    print "Report_Array",

    for count in range(report_count):


       print "["+ str(count)+ "]= "+ str(report_array[count]),

    print("\n")

    # Must ensure all "reports[xx]" are in "reported" state!
    report_counter= report_count- 1
    while (report_counter>= 0):

        print "Report_Array ["+ str(report_counter)+ "]= "+ str(report_array[report_counter]),

        while report_array[report_counter]!= 'reported':
            report_array= query_task_status()

#            print (".", end= "", flush= True)
            print ".",
            sys.stdout.flush()

            time.sleep(3)
        print ("")

        report_counter-=1

    for count in range(report_count):

        print ">Report_Array ["+ str(count)+ "]= "+ str(report_array[count]),
        print "\t",
    print ("")

    print "ID= "+ str(id),

    score= 0
    report_count= len(report_array)
    if id<= report_count:
         score= get_report_score(id)
    else:
         if report_count> 0:
              score= get_report_score(report_count)

    print("Score= "+ str(score))

    #delete_task([id])

    #Function will return true if score > 5 else return false
    # > 5 means its malicious and < 5 means its benign
    return score> 4.0,id

def submit_json (file_name,id):

	changes=[]
	url="http://192.168.2.222:8090/tasks/report/{}".format(id)
	r=(requests.get(url)).json()

	count=(len(r["signatures"]))

	b=0

	while(b<count):
		changes.append(r["signatures"][b]["description"])	
		b=b+1	

	score=r["info"]["score"]
	d={"name":file_name,"score":score,"signatures":[{'sig':key} for key in changes]}
	h=json.dumps(d,indent=1)
	
	save_name="{0}/results/{1}.json".format(path_os,file_name)
	
	with open(save_name,'w') as f:
		json.dump(h,f)
		
	headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
	p=requests.post(url="http://193.168.3.194:3000/",data=h,headers=headers)
	print ("Data send")
		
##### Start of the program
def Classifier():

    path="{0}/files/".format(path_os)
    cmd1="mkdir -p {}/results".format(path_os)
    os.system(cmd1)
	
    for i in os.listdir(path):
       file_send="{0}/files/{1}".format(path_os,i)
       print "Working on file {}".format(i)
       result,id=submit_query_report(file_send)
       
	   
       if id==-1:
           print "File {} is not submitted. Error in submission".format(i)
           continue		   
                         
       else:
               if (result==True):
                   print "File {} is malicious".format(i)
                   submit_json(i,id)
                   delete_task([id])
			   
               else:
                   print "File {} is not malicious".format(i)
                   submit_json(i,id)
                   delete_task([id])
		   		
    print "Process completed"	

Classifier()
	
