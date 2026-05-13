from dash import Input, Output, State, dash_table
from dashboardApp import app
import pandas as pd
import src.dashboardSubroutines as ds
import src.DH_Queries as dhq
import io
import json


sub_red = '#E74C3C'
sub_yellow = '#F4D03F'
sub_green = '#16A085' 


@app.callback(
        Output('submissionstore', 'data', allow_duplicate=True),
        Output('selectedsubmissionstore', 'data', allow_duplicate=True),
        Input(component_id='updatethis', component_property='n_clicks'),
        State(component_id='tierselector', component_property='value'),
        State(component_id='selectedsubmissionstore', component_property='data'),
        State(component_id='selectedstudytable', component_property='selected_rows'),
        State(component_id='submissionstore', component_property='data'),
        State(component_id='studyselector', component_property='value')
)
def updateInactiveTime(n_clicks, tierselector, selectedsubmissionstore, selected_rows, submissionstore, studyselector):
    if n_clicks >= 0:
        sub_df = pd.read_json(io.StringIO(selectedsubmissionstore), orient='split')
        selected_df = sub_df.iloc[selected_rows]
        for index, row in selected_df.iterrows():
            res = ds.updateSubmissionClock(row['_id'], tierselector)
          
        subjson = ds.apiQuery(tierselector, dhq.list_sub_query, {"status":["All"]})
        sub_df = pd.DataFrame(subjson['data']['listSubmissions']['submissions'])
        #Create the elapsedTime column
        sub_df = ds.elapsedTime(sub_df) 
        table_df = sub_df.loc[sub_df['studyAbbreviation'] == studyselector]
        return sub_df.reset_index().to_json(orient='split'), table_df.reset_index().to_json(orient='split')




@app.callback(
        Output("page-content", "children"),
        Input(component_id='selectedsubmissionstore', component_property='modified_timestamp'),
        State(component_id='selectedsubmissionstore', component_property='data')
)
def populateStudyInfoTable(modified_timestamp, selectedsubmissionstore):
    sub_df = pd.read_json(io.StringIO(selectedsubmissionstore),orient='split')
    data=sub_df.to_dict('records')
    #colors = {'new':'#3498DB' , 'error': '#E74C3C', 'warning': '#F4D03F', 'passed': '#16A085'}
    columns=[{"name":e, "id":e} for e in (sub_df.columns)]
    return dash_table.DataTable(id='selectedstudytable',
                                data=data, 
                                columns=columns, 
                                style_table={'overflowX':'auto'},
                                style_cell={'overflow':'hidden', 'textOverflow':'ellipsis', 'maxWidth':10, 'textAlign':'center'},
                                style_data={'color':'black', 'backgroundColor':'white'},
                                style_data_conditional=[{'if':{'row_index':'odd'}, 'backgroundColor': 'rgb(220,220,220)'},
                                                        {'if':{'filter_query':'{inactiveDays} <= 45', 'column_id':'inactiveDays'}, 'backgroundColor': sub_green, 'color':'black'},
                                                        {'if':{'filter_query':'{inactiveDays} >= 46 && {inactiveDays} <=59', 'column_id':'inactiveDays'}, 'backgroundColor': sub_yellow, 'color':'black'},
                                                        {'if':{'filter_query':'{inactiveDays} >= 60', 'column_id':'inactiveDays'}, 'backgroundColor': sub_red, 'color':'black'}],
                                style_header={'backgroundColor': 'rgb(210,210,210)', 'color':'black', 'fontWeight':'bold', 'textAlign':'center'},
                                row_selectable="multi",
                                sort_action='native',
                                sort_mode='multi',
                                tooltip_data=[
                                    {
                                        column:{'value': str(value), 'type':'markdown'}
                                        for column, value in row.items()
                                    } for row in sub_df.to_dict('records')
                                ],
                                tooltip_duration=None,
                                export_format="csv"
                                )



@app.callback(
    Output("datacontent", "children"),
    Input(component_id="dataselector", component_property="value"),
    State(component_id='submissionstore', component_property='data'),
    State(component_id='subselector', component_property="value"),
    State(component_id='tierselector', component_property='value'),
)
def populateDataTable(dataselector, submissionstore, subselector, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    idlist = sub_df.query("name == @subselector")['_id'].tolist()
    if len(idlist) >= 1:
        queryvars = {'_id':idlist[0], 'nodeType':dataselector, 'status':'All', 'first':-1, 'offset':0, 'orderBy':'studyID', 'sortDirection':'desc'}
        data_res = ds.apiQuery(tierselector, dhq.submission_nodes_query, queryvars)
        if 'data' in data_res:
            if data_res['data']['getSubmissionNodes']['total'] == 0:
                return dash_table.DataTable()
            else:
                data_df = pd.DataFrame(columns=data_res['data']['getSubmissionNodes']['properties'])
                for entry in data_res['data']['getSubmissionNodes']['nodes']:
                    data_df.loc[len(data_df)] = json.loads(entry['props'])
                return ds.buildBasicTable(data_df)
        else:
            return dash_table.DataTable()
    else:
        return dash_table.DataTable()



@app.callback(
    Output('errorcontent', 'children'),
    Input(component_id='errorselector', component_property='value'),
    State(component_id='submissionstore', component_property='data'),
    State(component_id='subselector', component_property='value'),
    State(component_id='tierselector', component_property='value'),
)
def errorDetailTable(errorselector, submissionstore, subselector, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    idlist = sub_df.query("name == @subselector")["_id"].tolist()
    if len(idlist)>=1:
        subvars = {"submissionID":idlist[0], "severity":"Error", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
        sub_res = ds.apiQuery(tierselector, dhq.summaryQuery, subvars)
        if sub_res['data']['aggregatedSubmissionQCResults']['total'] == 0:
            return dash_table.DataTable()
        else:   
            errorvars = {"id": idlist[0], "severities":"Error", "first": -1, "offset": 0, "orderBy":"displayID", "sortDirection":"desc"}
            detail_res = ds.apiQuery(tierselector, dhq.detailedQCQuery, errorvars)
            columns = ['type', 'title', 'description']
            error_df = pd.DataFrame(columns=columns)
            for result in detail_res['data']['submissionQCResults']['results']:
                #print(f"Starting results:\n{result}\n")
                for error in result['errors']:
                    #the following filter is needed because if an entity has more then one error, all are returned by the system.  That's a feature, not a bug.
                    if error['title'] == errorselector:
                        error['type'] = 'Error'
                        error_df.loc[len(error_df)] = error
            print(f"processed Errors:\n{error_df}")
            return ds.buildBasicTable(error_df)
    else:
        return dash_table.DataTable()


@app.callback(
        Output('warningcontent', 'children'),
        Input(component_id='warningselector', component_property='value'),
        State(component_id='submissionstore', component_property='data'),
        State(component_id='subselector', component_property='value'),
        State(component_id='tierselector', component_property='value')
)
def warningDetailTable(warningselector, submissionstore, subselector, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore), orient='split')
    idlist = sub_df.query("name == @subselector")["_id"].tolist()
    if len(idlist) >= 1:
        subvars = {"submissionID":idlist[0], "severity":"Warning", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
        sub_res = ds.apiQuery(tierselector, dhq.summaryQuery, subvars)
        if sub_res['data']['aggregatedSubmissionQCResults']['total'] == 0:
            return dash_table.DataTable()
        else:
            errorvars = {"id": idlist[0], "severities":"Warning", "first": -1, "offset": 0, "orderBy":"displayID", "sortDirection":"desc"}
            detail_res = ds.apiQuery(tierselector, dhq.detailedQCQuery, errorvars)
            # If Updating existing data is selected, we want to show both old and new, so that is handled differently
            if warningselector == 'Updating existing data':
                update_df = ds.buildUpdateDataframe(subid=idlist[0], tier=tierselector)
                if update_df is not None:
                    styles = ds.warningStyle(update_df)
                    return ds.buildBasicTable(update_df, styles)
                else:
                    return dash_table.DataTable()
            else:
                columns = ['type', 'title', 'description']
                warning_df = pd.DataFrame(columns=columns)
                for result in detail_res['data']['submissionQCResults']['results']:
                    for warning in result['warnings']:
                        if warning['title'] == warningselector:
                            warning['type'] = 'Warning'
                            warning_df.loc[len(warning_df)] = warning
                return ds.buildBasicTable(warning_df)
    else:
        return dash_table.DataTable()
        


@app.callback(
    Output("batchcontent", "children"),
    Input(component_id="subselector", component_property="value"),
    State(component_id='submissionstore', component_property='data'),
    State(component_id='tierselector', component_property='value')
)
def populateBatchTable(subselector, submissionstore, tierselector):
    submission_df = pd.read_json(io.StringIO(submissionstore), orient='split')
    idlist = submission_df.query("name == @subselector")["_id"].tolist()
    if len(idlist)>=1:
        queryvars = {"submissionID":idlist[0], "orderBy":"createdAt", "sortDirection":"DESC"}
        batch_res = ds.apiQuery(tierselector, dhq.list_batch_query, queryvars)
        if batch_res['data']['listBatches']['total'] == 0:
            return dash_table.DataTable()
        else:
            batch_df = pd.DataFrame(columns=list(batch_res['data']['listBatches']['batches'][0].keys()))
            for batch in batch_res['data']['listBatches']['batches']:
                batch_df.loc[len(batch_df)] = batch
            #Need to covert errors and files to string otherwise it borks the table
            batch_df['errors'] = batch_df['errors'].astype(str)
            batch_df['files'] = batch_df['files'].astype(str)
            return ds.buildBasicTable(batch_df)
    else:
        return dash_table.DataTable()


@app.callback(
    Output("validationerrorsummary", "children"),
    Input(component_id='subselector', component_property='value'),
    State(component_id='submissionstore', component_property='data'),
    State(component_id='tierselector', component_property='value'),
)
def validationErrorSummaryTable(subselector, submissionstore, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    idlist = sub_df.query("name == @subselector")["_id"].tolist()
    # TODO: Need to handle "Data File not found differently"
    if len(idlist) >= 1:
        subvars = {"submissionID":idlist[0], "severity":"Error", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
        sub_res = ds.apiQuery(tierselector, dhq.summaryQuery, subvars)
        if sub_res['data']['aggregatedSubmissionQCResults']['total'] == 0:
            return dash_table.DataTable()
        else:
            columns = ['type', 'title', 'description']
            error_df = pd.DataFrame(columns=columns)
            errorvars = {"id": idlist[0], "severities":"Error", "first": -1, "offset": 0, "orderBy":"displayID", "sortDirection":"desc"}
            detail_res = ds.apiQuery(tierselector, dhq.detailedQCQuery, errorvars)
            for result in detail_res['data']['submissionQCResults']['results']:
                for error in result['errors']:
                    if error['title'] == 'Data File not found':
                        message = "Missing data files, check error details page"
                    elif error['title'] == "Data file MD5 mismatch":
                        message = "MD5 mismathes, check error details page"
                    else:
                        message = ds.bracketParse(error['description'])
                    error_df.loc[len(error_df)] = {'type':'Error', 'title':error['title'], 'description':message}
            summary_df = error_df.groupby(['title', 'description']).size().reset_index().rename(columns={0:'count'}).sort_values(by='count', ascending=False)
            return ds.buildBasicTable(summary_df)
    else:
        return dash_table.DataTable()



@app.callback(
    Output("validationswarningsummary", "children"),
    Input(component_id='subselector', component_property='value'),
    State(component_id='submissionstore', component_property='data'),
    State(component_id='tierselector', component_property='value'),
)
def validationWarningSummaryTable(subselector, submissionstore, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    idlist = sub_df.query("name == @subselector")["_id"].tolist()
    if len(idlist) >= 1:
        subvars = {"submissionID":idlist[0], "severity":"Warning", "first":-1, "offset":0, "sortDirection": "desc", "orderBy": "displayID"}
        sub_res = ds.apiQuery(tierselector, dhq.summaryQuery, subvars)
        if sub_res['data']['aggregatedSubmissionQCResults']['total'] == 0:
            return dash_table.DataTable()
        else:
            columns = ['type', 'title', 'description']
            error_df = pd.DataFrame(columns=columns)
            errorvars = {"id": idlist[0], "severities":"Warning", "first": -1, "offset": 0, "orderBy":"displayID", "sortDirection":"desc"}
            detail_res = ds.apiQuery(tierselector, dhq.detailedQCQuery, errorvars)
            for result in detail_res['data']['submissionQCResults']['results']:
                for error in result['warnings']:
                    message = ds.bracketParse(error['description'])
                    error_df.loc[len(error_df)] = {'type':'Error', 'title':error['title'], 'description':message}
            temp_df = error_df.groupby(['title', 'description']).size().reset_index().rename(columns={0:'count'}).sort_values(by='count', ascending=False)
            summary_df = ds.updateAggregation(temp_df)
            summary_df = summary_df.sort_values(by='count', ascending=False)
            return ds.buildBasicTable(summary_df)
    else:
        return dash_table.DataTable()