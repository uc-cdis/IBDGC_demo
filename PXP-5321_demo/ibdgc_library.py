from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission
import pandas as pd

endpoint = "https://ibdgc.datacommons.io/"
auth = Gen3Auth(endpoint, refresh_file = "credentials.json")
sub = Gen3Submission(endpoint, auth)

summary_order = [
   "_center_count",
   "_participant_count",
   "_sample_count",
   "_raw_snp_genotype_count",
]

summary_count_headers = {
    "_participant_count": "Participants",
    "_center_count": "Centers",
    "_sample_count": "Samples",
    "_raw_snp_genotype_count": "Genotyping Files",
}

def get_projects():
    ''' Query list of projects '''
    
    query_txt = """query Project { project(first:0) {project_id}} """
   
    data = sub.query(query_txt) 
   
    projects = []
    for pr in data['data']['project']:
        projects.append(pr['project_id'])
    projects = sorted(projects)

    return projects

def query_summary_counts(projects=None):
    ''' Query summary counts for each data type'''
   
    if projects == None:
        projects = get_projects()
    elif not isinstance(projects,list):
        projects = [projects]
       
    dftotal = pd.DataFrame()
    for p in projects:
        query_txt = """query Counts ($projectID: [String]) {"""
        for param in summary_order:
            query_txt += """%s(project_id: $projectID)""" % param
        query_txt += "}" 
        variables = { 'projectID': p}
        data =  sub.query(query_txt, variables)
        indexes, values = [], []
        for key in summary_order:
            indexes.append(summary_count_headers[key])
            if key in data['data']:
                values.append(data['data'][key])
            else:
                values.append(0)           

        df = pd.DataFrame(values, index=indexes, columns=[p])
        if dftotal.empty:
            dftotal = df
        else:
            dftotal[p] = df[p]

    #dftotal = pd.concat(dftotal)    
 
    return dftotal


def query_counts_by_collection(project):
    """ make summary table reflecting how much data was submitted by each creator"""
    #Determine the number of participants in a project
    query_txt="""{
    _participant_count(project_id: "%s") 
    }"""%project
    participant_project_count=sub.query(query_txt)
    total_participants=participant_project_count['data']['_participant_count']
    # Gather center metadata, submitter_id, name, country and investigator_name
    participant_id=list()
    gender=list()
    diagnosis=list()
    ibd_affection_status=list()
    investigators = list()
    countries=list()
    center_submitter_id=list()
    for num in range(0,total_participants,1000):
        query_txt="""
            {participant(project_id: "%s", first: 1000,offset:%s) {
            submitter_id
            centers {
                investigator_name
                country
                submitter_id
            }
            demographics {gender}
            diagnoses {ibd_affection_status
                diagnosis}}
            }
            """%(project,num)
        data=sub.query(query_txt)
        collections=data['data']['participant']
        info="""Obtaining 1000 entities from offset %s for %s entries."""%(str(num),str(total_participants))
        print(info)
        for collection in collections:
            investigators.append(collection['centers'][0]['investigator_name'])
            countries.append(collection['centers'][0]['country'])
            center_submitter_id.append(collection['centers'][0]['submitter_id'])
            gender.append(collection['demographics'][0]['gender'])
            if collection['diagnoses']==[]:
                diagnosis.append("None")
            else:
                diagnosis.append(collection['diagnoses'][0]['diagnosis'])
            if collection['diagnoses']==[]:
                ibd_affection_status.append("None")
            else:
                ibd_affection_status.append(collection['diagnoses'][0]['ibd_affection_status'])
            participant_id.append(collection['submitter_id'])

    ziplist=list(zip(investigators,countries,center_submitter_id,gender,diagnosis,ibd_affection_status,participant_id))
    summary_df=pd.DataFrame(ziplist, columns = ["investigator","country","center_id","gender","diagnosis","ibd_affection_status","participant_id"])

    return summary_df

