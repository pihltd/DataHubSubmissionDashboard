# https://medium.com/@jasonyang.algo/getting-started-with-pyqt6-a-beginner-friendly-guide-to-modern-gui-development-79924151440f

import pandas as pd
import src.DH_Queries as dhq
import src.qtDHFunctions as dhf
from PyQt6.QtCore import QObject, pyqtSignal

class DataSignals(QObject):
    sub_updated = pyqtSignal()  # Submission datafram is updated

class SubmissionData(QObject):
    
    
    def __init__(self):
        self.study_df = pd.DataFrame()
        self.submission_df = pd.DataFrame()

        
    
    def getStudyInfo(self, url, apitoken, variables=None):
        #print('Starting Submission Info process')
        
        studyinfojson = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.org_query2, variables=variables)
        #print(f"Submissioninfojson: {submissioninfojson}")
        if studyinfojson is not None:
            loading = []
            for entry in studyinfojson['data']['listSubmissions']['submissions']:
                #print(f"Loading {entry}")
                #loading.append(entry)
                loading.append({"_id": entry['study']['_id'], 'studyAbbreviation': entry['study']['studyAbbreviation']})
            self.study_df = pd.DataFrame(loading)

       
    def getStudyList(self):
        return self.study_df['studyAbbreviation'].unique().tolist()
    
    
    def getSubmissionInfo(self, url, apitoken, abbrev, variables=None):
        
        submissioninfojson = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.list_sub_query, variables=variables)
        fullsubmission_df = pd.DataFrame(submissioninfojson['data']['listSubmissions']['submissions'])
        #self.submission_df = fullsubmission_df.query("studyAbbreviation == @abbrev")
        fullsubmission_df = fullsubmission_df.query("studyAbbreviation == @abbrev")
        self.submission_df = dhf.elapsedTime(fullsubmission_df)
        
        
        
    def getSubmissionDataFrame(self):
        return self.submission_df
    
    def getSubmissionList(self):
        return self.submission_df['name'].unique().tolist()
    
    
    def getErrorPieChartInfo(self, url, apitoken, submissionname, variables=None):
        sub_df = self.submission_df.query('studyAbbreviaion == @submission')
        subid = sub_df.at[0, "_id"]
        
        vars = {"submissionID":subid, "severity":"Error", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
        errorjson = dhf.dhApiQuery(url=url, apitoken=apitoken, query=dhq.list_sub_query, variables=vars)
        print(errorjson)
        
    
    def barChartCountData(self,url, apitoken, submissionname, variables=None):
        categories = ['new', 'error', 'warning', 'passed']
        columns = ['nodeName', 'total', 'new', 'error', 'warning', 'passed']
        
        idlist = self.submission_df.query("name == @submissionname")["_id"].tolist()
        if len(idlist) >= 1 :
            vars = {'id': idlist[0]}
            countjson = dhf.dhApiQuery(url=url, apitoken=apitoken, query= dhq.submission_stats_query, variables=vars)
            substats_df = pd.DataFrame(columns=columns)
            for entry in countjson['data']['submissionStats']['stats']:
                substats_df.loc[len(substats_df)] = entry
            #nodename = substats_df['nodeName'].tolist()
            #total = substats_df['total'].tolist()
            nodenamedict = {}
            totalcountlist = []
            count = 1
            for index, row in substats_df.iterrows():
                nodenamedict[count] = row['nodeName']
                totalcountlist.append(row['total'])
                count = count + 1
            return nodenamedict, totalcountlist
        else:
            return None, None
    
    def barChartCountData2(self,url, apitoken, submissionname, variables=None):
        categories = ['new', 'error', 'warning', 'passed']
        columns = ['nodeName', 'total', 'new', 'error', 'warning', 'passed']
                
        idlist = self.submission_df.query("name == @submissionname")["_id"].tolist()
        if len(idlist) >= 1 :
            vars = {'id': idlist[0]}
            countjson = dhf.dhApiQuery(url=url, apitoken=apitoken, query= dhq.submission_stats_query, variables=vars)
            substats_df = pd.DataFrame(columns=columns)
            for entry in countjson['data']['submissionStats']['stats']:
                substats_df.loc[len(substats_df)] = entry
            return substats_df
            
            #final = {}
            #for index, row in substats_df.iterrows():
            #    final[row['nodeName']] = {'new':row['new'], 'error': row['error'], 'warning': row['warning'], 'passed': row['passed']}
            #return final
        else:
            return None
    
        