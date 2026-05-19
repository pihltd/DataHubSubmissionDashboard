import requests
from datetime import datetime, timezone
import os 
from dash import dash_table
import json
import pandas as pd
import src.DH_Queries as dhq
from pytz import timezone as tz


def apiQuery(tier, query, variables, queryprint = False):
    if tier == 'DEV':
        url = 'https://hub-dev.datacommons.cancer.gov/api/graphql'
        token = os.environ['DEVAPI']
    elif tier == 'DEV2':
        url = 'https://hub-dev2.datacommons.cancer.gov/api/graphql'
        token = os.environ['DEV2API']
    elif tier == 'QA':
        url = 'https://hub-qa.datacommons.cancer.gov/api/graphql'
        token = os.environ['QAAPI']
    elif tier == 'QA2':
        url = 'https://hub-qa2.datacommons.cancer.gov/api/graphql'
        token = os.environ['QA2API']
    elif tier == 'STAGE':
        url = 'https://hub-stage.datacommons.cancer.gov/api/graphql'
        token = os.environ['STAGEAPI']
    elif tier == 'PROD':
        url = 'https://hub.datacommons.cancer.gov/api/graphql'
        token = os.environ['PRODAPI']
    elif tier == None:
        return("No tier specified")

    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        if variables is None:
            result = requests.post(url = url, headers = headers, json={"query": query})
            if queryprint:
                print(query)
        else:
            result = requests.post(url = url, headers = headers, json = {"query":query, "variables":variables})
            if queryprint:
                print(query)
                print(variables)
        if result.status_code == 200:
            return result.json()
        else:
            print(f"Error: {result.status_code}")
            return result.content
    except requests.exceptions.HTTPError as e:
        return(f"HTTP Error: {e}")


 
def elapsedTime(submission_df):
    days = []
    for index, row in submission_df.iterrows():
        temp = row['updatedAt'].split('T')
        update = datetime.strptime(temp[0], '%Y-%m-%d')
        update = update.replace(tzinfo=tz('UTC'))
        now = datetime.now(timezone.utc)
        diff = (now - update).days
        days.append(diff)
    submission_df.insert(8,'inactiveDays',days,True)
    return submission_df


def bracketParse(parsethis):
    if ']' in parsethis:
        first = parsethis.split("]")
        errorstring = first[1]
        if "[" in errorstring:
            second = errorstring.split("[")
            return second[0]
        else:
            return errorstring
    else:
        return parsethis


def updateAggregation(df):
    filelist = []
    columns = ['title', 'description', 'count']
    agg_df = pd.DataFrame(columns=columns)
    for index, row in df.iterrows():
        if 'Updating' in row['title']:
            filelist.append(row['description'])
        else:
            agg_df.loc[len(agg_df)] = row
    if len(filelist) > 0:
        agg_df.loc[len(agg_df)] = {'title': 'Updating existing data', 'description': 'File update', 'count': len(filelist)}
    return agg_df


def updateSubmissionClock(subid, tier):
    getSubmissionQuery = """
        query GetSubmissions(
            $id: ID!    
        ){
            getSubmission(_id:$id){
                _id
                name
                dataCommons
            }
        }

    """
    vars = {"id": subid}
    updatejson = apiQuery(tier, getSubmissionQuery, vars, False)
    return updatejson


def buildBasicTable(df, diffstyle = None):
    if diffstyle is None:
        styles = [{'if':{'row_index':'odd'}, 'backgroundColor': 'rgb(220,220,220)'}]
    else:
        styles = diffstyle

    return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": e, "id": e} for e in (df.columns)],
            style_table={'overflowX':'auto'},
            style_cell={'overflow':'hidden', 'textOverflow':'ellipsis', 'maxWidth':10, 'textAlign':'center'},
            style_data={'color':'black', 'backgroundColor':'white'},
            style_data_conditional=styles,
            style_header={'backgroundColor': 'rgb(210,210,210)', 'color':'black', 'fontWeight':'bold', 'textAlign':'center'},
            tooltip_data=[
                {
                    column:{'value': str(value), 'type':'markdown'}
                    for column, value in row.items()
                } for row in df.to_dict('records')
            ],
            tooltip_duration=None,
            export_format="csv"
        )


def warningStyle(df):
    styles = [{'if':{'row_index':'odd'}, 'backgroundColor': 'rgb(220,220,220)'}]
    for i in range(1, len(df), 2):
        curr_row = df.iloc[i]
        prev_row = df.iloc[i-1]
        for col in df.columns:
            if col != 'EntryType':
                if curr_row[col] != prev_row[col]:
                    styles.append({
                        'if': {'row_index': i, 'column_id': f"{col}"}, 'backgroundColor': '#3498DB', 'color':'black' 
                    })
    return styles



def diffDataFrame(subid, nodetype, nodeID, tier, query):
    # This is used to create a df for data update warnings
    difflist = []
    variables = {'submissionID': subid , 'nodeType': nodetype, 'nodeID': nodeID}
    diffres = apiQuery(tier, query, variables)
    dfcollection = {}
    if 'errors' in diffres:
        return None
    else:
        for entry in diffres['data']['retrieveReleasedDataByID']:
            tempstuff = json.loads(entry['props'])
            propstuff = {}
            if entry['status'] == "Warning":
                propstuff['EntryType'] = "New"
            else:
                propstuff['EntryType'] = 'Existing'
            for key, value in tempstuff.items():
                propstuff[key] = value
            temp_df = pd.DataFrame(propstuff, index=[entry['submissionID']])
            dfcollection[entry['submissionID']] = temp_df
            keylist = list(dfcollection.keys())
            if len(keylist) >= 2:
                df1 = dfcollection[keylist[0]]
                df2 = dfcollection[keylist[1]]
                diff_df = pd.concat([df1, df2]).drop_duplicates(keep=False)
                difflist.append(diff_df)
        report_df = pd.concat(difflist)
        return report_df



def buildUpdateDataframe(subid, tier):
    final_report_df = pd.DataFrame()
    #Get a list of the nodes in the submission
    subvars = {"submissionID": subid}
    sub_summary_res = apiQuery(tier=tier, query=dhq.submission_summary_query, variables=subvars)
    nodelist = []
    if 'getSubmissionSummary' in sub_summary_res['data']:
        for entry in sub_summary_res['data']['getSubmissionSummary']:
            nodelist.append(entry['nodeType'])
        # Now get the node ID for each of the nodes:
        node_data = {}
        for node in nodelist:
            vars = {"_id":subid, "nodeType":node, "status":"Warning", "first":-1, "offset":0, "orderBy":"nodes", "sortDirection":"Desc"}
            node_res = apiQuery(tier=tier, query=dhq.submission_nodes_query, variables=vars)
            if 'nodes' in node_res['data']['getSubmissionNodes']:
                for entry in node_res['data']['getSubmissionNodes']['nodes']:
                    node_data[node] = entry['nodeID']
            else:
                return None
            for node, nodeID in node_data.items():
                report_df = diffDataFrame(subid=subid, nodetype=node, nodeID=nodeID, tier=tier, query=dhq.retrieve_released_data_query)
                final_report_df = pd.concat([final_report_df, report_df]).drop_duplicates(keep=False)
        return final_report_df
    else:
        return None




def stsModelNodes(handle, version):
    url = f"https://sts.cancer.gov/v2/model/{handle}/version/{version}/nodes?skip=0&limit=0"
    print(url)
    headers = {'accept': 'application/json'}

    try:
        stsres = requests.get(url=url, headers=headers)
        if stsres.status_code == 200:
            print(stsres.json())
            nodelist = []
            for result in stsres.json():
                nodelist.append(result['handle'])
            return nodelist
        else:
            print(stsres)
            return []

    except requests.exceptions.HTTPError as e:
        return(f"HTTP Error: {e}")