from dash import Input, Output, State, html
from dashboardApp import app



@app.callback(
    Output("studytabletitle", "children"),
    Input(component_id='studyselector', component_property='value')
)
def changeStudyTableTitle(studyselector):
    if studyselector == None:
        return "Submissions for Study: None"
    else:
        return f"Submissions for Study: {studyselector}"


@app.callback(
    Output("submissionstatusplottitle", "children"),
    Input(component_id='subselector', component_property='value')
)
def changeSubmissionStatusPlotTitle(subselector):
    if subselector == None:
        return "Submission Status by Count"
    else:
        return f"Submission Status by Count: {subselector}"


@app.callback(
    Output("submissionPercentstatusplottitle", "children"),
    Input(component_id='subselector', component_property='value')
)
def changeSubmissionStatusPercentageTitle(subselector):
    if subselector == None:
        return "Submission Status by Percentage"
    else:
        return f"Submission Status by Percentage: {subselector}"


@app.callback(
    Output('validationerrorpietitle', "children"),
    Input(component_id='subselector', component_property='value')
)
def changeValidationErrorPieTitle(subselector):
    if subselector == None:
        return "Validation Errors"
    else:
        return f"Validation Errors: {subselector}"


@app.callback(
    Output('validationwarningpietitle', "children"),
    Input(component_id='subselector', component_property='value')
)
def changeValidationWarningPieTitle(subselector):
    if subselector == None:
        return("Validation Warnings")
    else:
        return f"Validation Warnings: {subselector}"


@app.callback(
    Output("errortitle", "children"),
    Input(component_id="errorselector", component_property='value'),
    State(component_id="studyselector", component_property="value"),
    State(component_id="subselector", component_property="value")
)
def errorTableTitle(errorselector, studyselector, subselector):
    if errorselector == None:
        return("Error Details:")
    else:
        return ("Error Details:",html.Br(),"Study: "+studyselector,html.Br(),"Submission: "+subselector, html.Br(), "Errors: "+errorselector)


@app.callback(
Output("warningtitle", "children"),
Input(component_id='warningselector', component_property='value'),
State(component_id='studyselector', component_property='value'),
State(component_id='subselector', component_property='value')
)
def warningTableTitle(warningselector, studyselector, subselector):
    if warningselector == None:
        return("Warning Details:")
    else:
        return ("Warning Details:",html.Br(),"Study: "+studyselector,html.Br(),"Submission: "+subselector, html.Br(), "Warnings: "+warningselector)


@app.callback(
    Output("datatitle", "children"),
    Input(component_id="dataselector", component_property='value'),
    State(component_id="studyselector", component_property="value"),
    State(component_id="subselector", component_property="value")
)
def dataTableTitle(dataselector, studyselector, subselector):
    if dataselector == None:
        return ("Submitted Data:")
    else:
        return ("Submitted Data:",html.Br(),"Study: "+studyselector,html.Br(),"Submission: "+subselector, html.Br(), "Node: "+dataselector)

@app.callback(
    Output("batchtitle", "children"),
    Input(component_id="subselector", component_property="value")
)
def batchTableTitle(subselector):
    if subselector == None:
        return ("Batch History for Submission")
    else:
        return(f"Batch History for Submission: {subselector}")