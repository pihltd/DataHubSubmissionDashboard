from dash import Input, Output, State
from dashboardApp import app
import pandas as pd
import io
import src.dashboardSubroutines as ds
import src.DH_Queries as dhq
from dash.exceptions import PreventUpdate

@app.callback(
    Output("studyselector", "options"),
    Input(component_id='studystore', component_property='data')
)
def populateStudyDropdown(studystore):
    study_df = pd.read_json(io.StringIO(studystore), orient='split')
    return study_df['studyAbbreviation'].unique()


# Submissions Selector
@app.callback(
    Output("subselector", "options"),
    Input(component_id='studyselector', component_property='value'),
    State(component_id='submissionstore', component_property='data')
)
def populateSubmissionDropdown(studyselector, submissionstore):
    if studyselector is None:
        raise PreventUpdate
    else:
        sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
        temp_df=sub_df[sub_df['studyAbbreviation'] == studyselector]
        return temp_df['name'].unique()



# Error Selector
@app.callback(
    Output('errorselector', 'options'),
    Input(component_id='subselector', component_property='value'),
    State(component_id='submissionstore', component_property='data'),
    State(component_id='tierselector', component_property='value'),
)
def populateErrorSelector(subselector, submissionstore, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore), orient='split')
    idlist = sub_df.query("name == @subselector")["_id"].tolist()
    if len(idlist)>=1:
        #queryvars = {"submissionID":idlist[0], "severity":"All", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
        queryvars = {"submissionID":idlist[0], "severity":"Error", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
        selector_res = ds.apiQuery(tierselector, dhq.summaryQuery, queryvars)
        if selector_res['data']['aggregatedSubmissionQCResults']['total'] == 0:
            return []
        else:
            val_df = pd.DataFrame(selector_res['data']['aggregatedSubmissionQCResults']['results'])
            return val_df['title'].unique()
    else:
        return []
    
#Warning Selector
@app.callback(
        Output('warningselector', 'options'),
        Input(component_id='subselector', component_property='value'),
        State(component_id='submissionstore', component_property='data'),
        State(component_id='tierselector', component_property='value')
)
def populateWarningSelector(subselector, submissionstore, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore), orient='split')
    idlist = sub_df.query("name ==@subselector")["_id"].tolist()
    if len(idlist) >= 1:
        queryvars = {"submissionID":idlist[0], "severity":"Warning", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
        selector_res = ds.apiQuery(tierselector, dhq.summaryQuery, queryvars)
        if selector_res['data']['aggregatedSubmissionQCResults']['total'] == 0:
            return []
        else:
            val_df = pd.DataFrame(selector_res['data']['aggregatedSubmissionQCResults']['results'])
            return val_df['title'].unique()
    else:
        return []


# Data Node selector
@app.callback(
    Output('dataselector', 'options'),
    Input(component_id='subselector', component_property='value'),
    State(component_id='submissionstore', component_property='data'),
    State(component_id='tierselector', component_property='value'),
)
def populateNodeSelector(subselector, submissionstore, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    idlist = sub_df.query("name == @subselector")["_id"].tolist()
    if len(idlist) >= 1:
        queryvars = {'id':idlist[0]}
        selector_res = ds.apiQuery(tierselector, dhq.submission_stats_query, queryvars)
        temp = []
        for entry in selector_res['data']['submissionStats']['stats']:
            temp.append(entry['nodeName'])
        return temp
    else:
        return []