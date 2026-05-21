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
        return {'handle':model, 'version': modelversion, 'nodes':nodelist, 'submissionid':idlist[0]}


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
    return dcc.RadioItems(modelstore['nodes'], id='noderadio')



@app.callback(
    Output('deletedatastore', 'data', allow_duplicate=True),
    Input(component_id='fileupload', component_property='contents'),
    State('fileupload', 'filename'),
)
def loadDeleteDatastore(contents, filename):
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


@app.callback(
    Output('deletedatastore', 'data', allow_duplicate=True),
    Input('nukefromorbit', 'n_clicks'),
    State('deletedatastore', 'data'),
    State('modelstore', 'data'),
    State('noderadio', 'value'),
    #State('subselector', 'value'),
    State('submissionstore', 'data'),
    State('tierselector', 'value')
)
def nukeFromOrbit(n_clicks, deletedatastore,modelstore,  nodeoptions, submissionstore, tierselector):
    submission_df = pd.read_json(io.StringIO(submissionstore), orient='split')
    #idlist = submission_df.query("name == @subselector")['_id'].tolist()
    #submissionid = idlist[0]
    delete_df = pd.read_json(io.StringIO(deletedatastore), orient='split')
    if len(delete_df) > 0:
        # Need the key field for the node
        keyfield = ds.stsKeyProperty(modelhandle=modelstore['handle'], modelversion=modelstore['version'], nodename=nodeoptions)
        # Check that the key field is in the delete dataframe
        if keyfield in delete_df.columns:
            deletelist = delete_df[keyfield].unique().tolist()

            deletevars = {"_id": modelstore['submissionid'], 
                      "nodeType": nodeoptions,
                      "nodeIds": deletelist,
                      "deleteAll": False,
                      "exclusiveIds": None
            }

            delres = ds.apiQuery(tierselector, dhq.deleteQuery, deletevars)
            print(f"Delete result message: {delres}")

        else:
            print(f"Key field {keyfield} not in {delete_df.columns.tolist()}")

    return None


# TODO:  Provide available node list (radio buttons?)
# Upload deletion sheet
# Display "This is what's going bye-bye, click to confirm"
# Nuke from orbit