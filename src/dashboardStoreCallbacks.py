from dash import Input, Output, State
from dashboardApp import app
import src.dashboardSubroutines as ds
import src.DH_Queries as dhq
import pandas as pd
import io



@app.callback(
    Output('studystore', 'data'),
    Input(component_id='tierselector', component_property='value'),
)
def populateStudyStore(tierselector):
    studyjson = ds.apiQuery(tierselector, dhq.org_query2, None)
    studylist = []
    tracker = []
    for entry in studyjson['data']['listSubmissions']['submissions']:
        if entry['study']['_id'] not in tracker:
            studylist.append({"_id": entry['study']['_id'], 'studyAbbreviation': entry['study']['studyAbbreviation']})
            tracker.append(entry['study']['_id'])
    study_df = pd.DataFrame(studylist)
    return study_df.reset_index().to_json(orient='split')


@app.callback(
    Output('submissionstore', 'data', allow_duplicate=True),
    Input(component_id='studystore', component_property='data'),
    State(component_id='studyselector', component_property='value'),
    State(component_id='tierselector', component_property='value'),
)
def populateSubmissionStore(studystore, studyselector, tierselector):
    #Get a list of the submissions
    subjson = ds.apiQuery(tierselector, dhq.list_sub_query, {"status":["All"]})
    sub_df = pd.DataFrame(subjson['data']['listSubmissions']['submissions'])
    #Create the elapsedTime column
    sub_df = ds.elapsedTime(sub_df) 
    return sub_df.reset_index().to_json(orient='split')


@app.callback(
        Output('selectedsubmissionstore', 'data', allow_duplicate=True),
        Input(component_id='studyselector', component_property='value'),
        State(component_id='submissionstore', component_property='data')
)
def populateSelectedSubmissionStore(studyselector, submissionstore):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    table_df = sub_df.loc[sub_df['studyAbbreviation'] == studyselector]
    return table_df.reset_index().to_json(orient='split')