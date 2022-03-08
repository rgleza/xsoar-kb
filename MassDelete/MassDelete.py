''' IMPORTS '''
import json
import requests
import time
requests.packages.urllib3.disable_warnings()
# ''' GLOBALS/PARAMS '''
SERVER_URL ="https://192.168.0.1" ######## Demisto URL
TOKEN_MY_VM = "1234123412341234123412341231234D" ####### Demisto API KEY
HEADERS = {
    'Authorization': TOKEN_MY_VM,
    'Content-Type': 'application/json'
}
PATH = "/incidents/search"  # ''' Endpoint to Search  Incidents '''
###################
### Variables ##########
TYPE_OF_INCIDENT="Unclassified"

################################
############THROTTLING VARIABLES
################################
INCIDENTS_TOTAL = 5 # Total amount of incidents to be deleted at a time (BATCH)
WAIT_TIME = 3      # Sleep time to wait for the server after each deletion
DAYS_SEARCH= 30  # Days back in the search you are performing


#### The following query will search for:
        # Incidentes Type: TYPE_OF_INCIDSENT
        # Over the past X Days
        # It doesn't matter size or page since we only want the total of Incidents
initialQuery = {"filter":{"page":0,"size":1,"query":"type:"+TYPE_OF_INCIDENT, "period":{"by":"day","fromValue":DAYS_SEARCH}}}
           # {"filter":{"query":"-status:closed -category:job","period":{"by":"day","fromValue":7}}}
''' Performing Initial Search via API'''
res = requests.request(
    method='POST',
    url=SERVER_URL+PATH,
    data=json.dumps(initialQuery),
    headers=HEADERS,
    verify=False    # Certificate check disabled
    )
'''Verifyin' the request provided a valid code'''
if not res.ok:
    print("Error: Verify your request:\n " + res.text)
json_data = json.loads(res.text)
totalIncidentsInt = json_data["total"] + 0 #This brings the TOTAL of results generated by the query as an Integer

#This query will get all the IDs that are going to be Deleted
################################
#################################
incident = {"filter":{"page":0,"size":totalIncidentsInt,"query":"type:"+TYPE_OF_INCIDENT, "period":{"by":"day","fromValue":DAYS_SEARCH}}}
res = requests.request(
    method='POST',
    url=SERVER_URL+PATH,
    data=json.dumps(incident),
    headers=HEADERS,
    verify=False    # Certificate check disabled
    )
if not res.ok:
    print("Error: Verify your request:\n " + res.text)
json_data = json.loads(res.text)


#### The following section will perform the actual DELETE of all the incidents
done=0
deletedIDRange=[]
while (done < totalIncidentsInt):
    deletedIDRange.append(str(json_data["data"][done]["id"])) ### Creating a List with all the Incident IDs that are going to be Deleted
    done += 1
    ### THROTLING at every 10 or 100 or 1000 It's up to you.
    if done % INCIDENTS_TOTAL == 0 and done !=0:
        PATHDELETE = "/incident/batchDelete"
        incidentdelete = {"ids":deletedIDRange,"filter":{"page":0,"size":100}}
        ### Sending the API Request to DELETE the incidents
        res2 = requests.request(
            method='POST',
            url=SERVER_URL+PATHDELETE,
            data=json.dumps(incidentdelete),
            headers=HEADERS,
            verify=False    # Certificate check disabled
            )
        '''Verifyin' that API sent provided a valid code'''
        if not res2.ok:
            print("Error: Verify your request:\n " + res.text)
        json_datas = json.loads(res2.text)
        time.sleep(WAIT_TIME) #Wait for 10,100, 1000  seconds
        print ("Deleting the following batch of  incidents --> " + str(deletedIDRange))
        deletedIDRange=[] #Cleaning  the array for the next iteration
#Deleting the last BATCH of Incidentes
PATHDELETE = "/incident/batchDelete"
incidentdelete = {"ids":deletedIDRange,"filter":{"page":0,"size":100}}
### Sending the API Request to DELETE the incidents
res2 = requests.request(
    method='POST',
    url=SERVER_URL+PATHDELETE,
    data=json.dumps(incidentdelete),
    headers=HEADERS,
    verify=False    # Certificate check disabled
    )
'''Verifyin' that API sent provided a valid code'''
if not res2.ok:
    print("Error: Verify your request:\n " + res.text)
json_datas = json.loads(res2.text)
print ("Deleting the LAST batch of  incidents --> " + str(deletedIDRange))
