# https://dash-resources.com/dash-callbacks-best-practices-with-examples/

from dash import Dash, html, dcc

from src.dashboardComponents import *
from src.dashboardStyles import *
from src.dashboardSubroutines import *


app = Dash(
    __name__,
    #external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True,
    update_title="Updating..."
)
app.title ="CRDC Submission Dashboard"

app.layout = html.Div([
    dcc.Store(id='studystore'),
    dcc.Store(id='submissionstore'),
    dcc.Store(id='selectedsubmissionstore'),
    dcc.Store(id="deletedatastore"),
    dcc.Store(id='modelstore'),
    sidebar, sitecontent
])


from src.dashboardDropDownCallbacks import *
from src.dashboardGraphicsCallbacks import *
from src.dashboardStoreCallbacks import *
from src.dashboardTitleCallbacks import *
from src.dashboardTableCallbacks import *
from src.dashboardDeleteCallbacks import *


if __name__ == "__main__":
    app.run(port=8050, debug=True)

