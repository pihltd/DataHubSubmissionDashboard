from dash import Input, Output, State, dcc
from dashboardApp import app
import pandas as pd
import io
import src.dashboardSubroutines as ds
import src.DH_Queries as dhq
import base64


@app.callback(
        Output('modelstore', 'data'),
        Input('deletesubinfo', 'n_clicks'),
        State('selectedsubmissionstore', 'data'),
        State('subselector', 'value'),
        State('tierselector', 'value'),
)
def updateModelStore(n_clicks, submissionstore, subselector, tierselector):
    sub_df = pd.read_json(io.StringIO(submissionstore),orient='split')
    idlist = sub_df.query("name == @subselector")['_id'].tolist()
    if len(idlist)>=1:
        vars = {'id': idlist[0]}
        results = ds.apiQuery(tier=tierselector, query=dhq.getModelQuery, variables=vars)
        model = results['data']['getSubmission']['dataCommons']
        modelversion = results['data']['getSubmission']['modelVersion']
        nodelist = ds.stsModelNodes(model, modelversion)
        return {'handle':model, 'version': modelversion, 'nodes':nodelist}


@app.callback(
    Output(component_id='deletetitle', component_property='children'),
    Input(component_id="modelstore", component_property='data'),
    State(component_id='selectedsubmissionstore', component_property='data'),
    State(component_id='subselector', component_property="value"),
    State(component_id='tierselector', component_property='value')
)
def deleteTitleUpdate(modelstore, submissionstore, subselector, tierselector):
    return(f"Delete Data using model {modelstore['handle']} version {modelstore['version']}")



@app.callback(
        Output('nodeoptions', 'children'),
        Input('modelstore', 'data')
)
def addRadio(modelstore):
    return dcc.RadioItems(modelstore['nodes'])



@app.callback(
    Output('deletedatastore', 'data'),
    Input(component_id='fileupload', component_property='contents'),
    State('fileupload', 'filename'),
)
def loadDeleteDatastore(contents, filename):
    print(f"Contents:\n{contents}\nFilename:\t{filename}\n")
    if contents is not None:
        content_type, content_string = contents.split(",")
        decoded_content = base64.b64decode(content_string)
        delete_df = pd.read_csv(io.StringIO(decoded_content.decode("utf-8")), sep="\t")
        return delete_df.reset_index().to_json(orient='split')

@app.callback(
    Output('deletetablecontent', 'children'),
    Input('deletedatastore', 'data')
)
def loadDeleteTable(data):
    delete_df = pd.read_json(io.StringIO(data), orient='split')
    return ds.buildBasicTable(delete_df)

# TODO:  Provide available node list (radio buttons?)
# Upload deletion sheet
# Display "This is what's going bye-bye, click to confirm"
# Nuke from orbit