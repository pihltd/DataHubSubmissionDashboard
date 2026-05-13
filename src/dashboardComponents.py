from dash import html, dcc
import src.dashboardStyles as ds


sidebar = html.Div(
    [
        html.H2("Data Hub", className="display-4"),
        html.Hr(),
        html.Div( 
            className='studydropdown',
            children=[
                #Tier Dropdown
                html.Hr(),
                html.H2("Tiers"),
                html.Hr(),
                html.P(
                    "Select a tier"
                ),
                html.Hr(),
                dcc.Dropdown(
                    id = 'tierselector',
                    options = ['DEV','DEV2','QA','QA2','STAGE', 'PROD'],
                    multi = False,
                    style={'backgroundcolor':'1E1E1E'},
                ),
                # Study Dropdown
                html.Hr(),
                html.H2("Studies"),
                html.Hr(),
                html.P(
                    'Select a Study'
                ),
                html.Hr(),
                dcc.Dropdown(
                    id='studyselector',
                    options=[],
                    multi=False,
                    style={'backgroundcolor':'1E1E1E'},
                ),
                # Submission Dropdown
                html.Hr(),
                html.H2("Submissions"),
                html.Hr(),
                html.P("Select a submission"),
                html.Hr(),
                dcc.Dropdown(
                    id='subselector',
                    options=[],
                    multi=False,
                    style={'backgroundcolor': '1E1E1E'},
                ),
                # Error Dropdown
                html.Hr(),
                html.H2("Error Details"),
                html.Hr(),
                html.P("Select an error type"),
                html.Hr(),
                dcc.Dropdown(
                    id='errorselector',
                    options = [],
                    multi=False,
                    style={'backgroundcolor': '1E1E1E'},
                ),
                # Warning Dropdown
                html.Hr(),
                html.H2("Warning Details"),
                html.Hr(),
                html.P("Select a warning type"),
                html.Hr(),
                dcc.Dropdown(
                    id = 'warningselector',
                    options = [],
                    multi=False,
                    style={'backgroundcolor': '1E1E1E'}
                ),
                # Data Dropdown
                html.Hr(),
                html.H2('Data Nodes'),
                html.Hr(),
                html.P("Select a data node"),
                html.Hr(),
                dcc.Dropdown(
                    id = 'dataselector',
                    options=[],
                    multi=False,
                    style={'backgroundcolor':'1E1E1E'}
                ),
            ],
            style={'color':'1E1E1E'}
        ),
    ],
    style=ds.SIDEBAR_STYLE,
)



tableheader = html.Div([
    html.Hr(),
    html.H2("Submissions for Study: Select a tier and study from the dropdowns", id='studytabletitle'),
    html.Hr()
    ]
)



errorheader = html.Div(
    [
        html.Hr(),
        html.H2("Error and Warning Details", id='errortitle'),
        html.Hr()
    ]
)



barcharts2 = html.Div([
    dcc.Loading([
        html.Div(
            #Count bar chart
            className='submissionStatusPlot',
            children=[
                html.Hr(),
                html.H2("Submission Status by Count", id='submissionstatusplottitle'),
                dcc.Graph(id='submissionstatusplot')
            ],
            style={'width':'49%', 'display':'inline-block'},
        ),
        html.Div(
            # Percentage bar chart
            className='submissionStatusPlotPercentage',
            children=[
                html.Hr(),
                html.H2("Submission Status by Percentage", id="submissionPercentstatusplottitle"),
                dcc.Graph(id="submissionPercentstatusplot")
            ],
            style={'width':'49%', 'display':'inline-block'},
        ),
    ])
])



errorpie2 = html.Div([
    dcc.Loading([
        html.Div(
            className='ValidationErrorPieChart',
            children=[
                html.Hr(),
                html.H2("Validation Errors", id='validationerrorpietitle'),
                dcc.Graph(id='validationErrorPie')
            ],
            style={'width':'49%', 'display': 'inline-block'},
        ),
        html.Div(
            className="ValidationWarningPieChart",
            children=[
                html.Hr(),
                html.H2("Validation Warnings", id='validationwarningpietitle'),
                dcc.Graph(id='validationWarningPie')
            ],
            style={'width':'49%', 'display':'inline-block'},
        )
    ])
])


errorsummary2 = html.Div([
    dcc.Loading([
        html.Div(
            className='ErrorSummaryTable',
            children=[
                html.Hr(),
                html.H2("Validation Error Summary"),
                html.Div(id="validationerrorsummary")
            ],
            style={'width':'49%', 'display':'inline-block'},
        ),
        html.Div(
            className='WarningSummaryTable',
            children=[
                html.Hr(),
                html.H2("Validation Warning Summary"),
                html.Div(id='validationswarningsummary')
            ],
            style={'width': '49%','display':'inline-block'},
        ),
    ])
])


dataheader = html.Div(
    [
        html.Hr(),
        html.H2("Submitted Data", id='datatitle'),
        html.Hr()
    ]
)

warningheader = html.Div([
    html.Hr(),
    html.H2("Validation Warnings", id='warningtitle'),
    html.Hr()
])

batchheader = html.Div(
    [
        html.Hr(),
        html.H2("Batch History", id="batchtitle"),
        html.Hr()
    ]
)

batchcontent2 = html.Div([
    dcc.Loading([
        html.Div(id="batchcontent")
    ])
])


content = html.Div([
    html.Div(id='page-content'),
])

updateButton = html.Button('Reset Time on Selected Submissions', id='updatethis', n_clicks=0)

errorcontent2 = html.Div([
    dcc.Loading([
        html.Div(id="errorcontent")
    ])
])

warningcontent = html.Div([
    dcc.Loading([
        html.Div(id='warningcontent')
    ])
])


datacontent2 = html.Div([
    dcc.Loading([
        html.Div(id="datacontent")
    ])
])


# https://stackoverflow.com/questions/70352045/dash-keep-tabs-bar-on-top-and-remember-where-was-scrolled-between-tabs
# The id = tabs-container points to tabs.css in the assets folder and makes the tabs sticky at the top
sitecontent =html.Div([
    dcc.Tabs(
    id='tabs-container', 
    value='tab-status',
    children=[
        dcc.Tab(label="Status",
                value = 'tab-status',
                id = 'statustab',
                style = ds.TAB_STYLE,
                selected_style = ds.SELECTED_TAB_STYLE,
                children=[tableheader, content, updateButton, barcharts2, errorpie2, errorsummary2],
                ),
        dcc.Tab(label="Submission Batch History",
                value="tab-batch",
                id='batchtab',
                style=ds.TAB_STYLE,
                selected_style=ds.SELECTED_TAB_STYLE,
                children=[batchheader, batchcontent2]
                ),
        dcc.Tab(label="Submission Errors",
                value = 'tab-errors',
                id = 'errortab',
                style = ds.TAB_STYLE,
                selected_style = ds.SELECTED_TAB_STYLE,
                children=[errorheader, errorcontent2]
                ),
        dcc.Tab(label='Submission Warnings',
                value = 'warning-data',
                id = 'warningtab',
                style=ds.TAB_STYLE,
                selected_style=ds.SELECTED_TAB_STYLE,
                children=[warningheader, warningcontent]),
        dcc.Tab(label="Submitted Data",
                value='tab-data',
                id='datatab',
                style=ds.TAB_STYLE,
                selected_style=ds.SELECTED_TAB_STYLE,
                children=[dataheader, datacontent2]
                )
        ]
    )
],style=ds.CONTENT_STYLE)