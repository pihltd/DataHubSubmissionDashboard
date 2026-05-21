from dash import Input, Output, State
from dashboardApp import app
import plotly.express as px
import pandas as pd
import src.dashboardSubroutines as ds
import io
import src.DH_Queries as dhq

sub_blue = '#3498DB' 
sub_red =  '#E74C3C'
sub_yellow = '#F4D03F'
sub_green =  '#16A085'

@app.callback(
    Output('validationErrorPie', 'figure'),
    Input(component_id='subselector', component_property='value'),
    State(component_id='submissionstore', component_property='data'),
    State(component_id='tierselector', component_property='value'),
)
def validationErrorPieChart(subselector, submissionstore, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    idlist = sub_df.query("name == @subselector")["_id"].tolist()
    #colors = {'new':'blue', 'error': 'red', 'warning':'yellow', 'passed':'green'}
    if len(idlist)>=1:
        valvars = {"submissionID":idlist[0], "severity":"Error", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
        val_res = ds.apiQuery(tierselector, dhq.summaryQuery, valvars)
        if val_res['data']['aggregatedSubmissionQCResults']['total'] == 0:
            return  px.pie()
        else:
            val_df = pd.DataFrame(val_res['data']['aggregatedSubmissionQCResults']['results'])
            return px.pie(val_df, values='count', names='title', hole=.3)
    else:
        return px.pie()



@app.callback(
    Output('validationWarningPie', 'figure'),
    Input(component_id='subselector', component_property='value'),
    State(component_id='submissionstore', component_property='data'),
    State(component_id='tierselector', component_property='value'),
)
def validationWarningPieChart(subselector, submissionstore, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    idlist = sub_df.query("name == @subselector")["_id"].tolist()
    #colors = {'new':'blue', 'error': 'red', 'warning':'yellow', 'passed':'green'}
    if len(idlist)>=1:
        valvars = {"submissionID":idlist[0], "severity":"Warning", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
        val_res = ds.apiQuery(tierselector, dhq.summaryQuery, valvars)
        if val_res['data']['aggregatedSubmissionQCResults']['total'] == 0:
            return  px.pie()
        else:
            val_df = pd.DataFrame(val_res['data']['aggregatedSubmissionQCResults']['results'])
            return px.pie(val_df, values='count', names='title', hole=.3)
    else:
        return px.pie()



@app.callback(
    Output('submissionstatusplot', 'figure'),
    Input(component_id="subselector", component_property="value"),
    State(component_id='submissionstore', component_property='data'),
    State(component_id='tierselector', component_property='value'),
)
def subStatusChart(subselector, submissionstore, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    idlist = sub_df.query("name == @subselector")["_id"].tolist()
    #colors = {'new':'blue', 'error': 'red', 'warning':'yellow', 'passed':'green'}
    colors = {'new': sub_blue , 'error': sub_red, 'warning': sub_yellow, 'passed': sub_green}
    #colors = {'new':'#3498DB' , 'error': '#E74C3C', 'warning': '#F4D03F', 'passed': '#16A085'}
    if len(idlist) >= 1:
        qvars = {'id': idlist[0]}
        query_res = ds.apiQuery(tierselector, dhq.submission_stats_query, qvars)
        columns = ['nodeName', 'total', 'new', 'error', 'warning', 'passed']
        substats_df = pd.DataFrame(columns=columns)
        for entry in query_res['data']['submissionStats']['stats']:
            substats_df.loc[len(substats_df)] = entry
        return px.bar(substats_df, x='nodeName', y=['new', 'error', 'warning', 'passed'], color_discrete_map=colors)
    else:
        return px.bar()



@app.callback(
    Output("submissionPercentstatusplot", "figure"),
    Input(component_id="subselector", component_property="value"),
    State(component_id="submissionstore", component_property="data"),
    State(component_id="tierselector", component_property="value")
)
def subStatusPercentageChart(subselector, submissionstore, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    idlist = sub_df.query("name == @subselector")["_id"].tolist()
    colors = {'new': sub_blue , 'error': sub_red, 'warning': sub_yellow, 'passed': sub_green}
    if len(idlist) >=1:
        qvars = {'id':idlist[0]}
        query_res = ds.apiQuery(tierselector, dhq.submission_stats_query, qvars)
        columns = ['nodeName', 'total', 'new', 'error', 'warning', 'passed']
        substats_df = pd.DataFrame(columns=columns)
        for entry in query_res['data']['submissionStats']['stats']:
            substats_df.loc[len(substats_df)] = entry
        #Add percentages to df
        calccolumns = columns = ['new', 'error', 'warning', 'passed']
        newcol = ['nodeName', 'new', 'error', 'warning', 'passed']
        per_df = pd.DataFrame(columns=newcol)
        for index, row in substats_df.iterrows():
            newrow = {}
            newrow['nodeName'] = row['nodeName']
            for column in calccolumns:
                if row['total'] > 0:
                    newrow[column] = (row[column]/row['total'])*100
                else:
                    newrow[column] = 0
            per_df.loc[len(per_df)] = newrow

        return px.bar(per_df, x='nodeName', y=['new', 'error', 'warning', 'passed'], color_discrete_map=colors)
    else:
        return px.bar()