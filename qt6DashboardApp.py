from PyQt6.QtWidgets import QApplication,  QMainWindow, QTabWidget, QVBoxLayout, QComboBox, QHBoxLayout, QWidget, QTableView, QLabel, QHeaderView
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor
#from PyQt6.QtCharts import QChart, QChartView, QPieSeries
#from PySide6.QtCharts import QChart, QChartVie


import pyqtgraph as pg

import pandas as pd
import numpy as np

from src.qtDHFunctions import dhAPICreds
from src.qtSubclasses import CustomDialog, SubmissionTableModel, PieCanvas
from src.qtData import SubmissionData

from layout_color_widget import Color

class MainWindow(QMainWindow):
    
    #TODO: Need reset methods when different drop-downs are changed so that things get cleared.
    # When Submission changes, re-do summary table
    # When Project changes, clera and reload Submission table and any submission related data
    # When tier changes, reset everything
    #TODO Spinners

    
    def __init__(self):
        super().__init__()
        
        self.submission_df = pd.DataFrame()
        self.theDataThing = SubmissionData()
        
        self.creds = None
        
        self.sub_blue = '#3498DB' 
        self.sub_red =  '#E74C3C'
        self.sub_yellow = '#F4D03F'
        self.sub_green =  '#16A085'
        self.tab_color = '#05ABED'
        
        
        self.setWindowTitle("CRDC Dashboard")
        
        #
        #  Layouts
        #
        summarylayout = QVBoxLayout()
        dropdownlayout = QHBoxLayout()
        barlayout = QHBoxLayout()
        self.pielayout = QHBoxLayout()
        errorlayout = QVBoxLayout()
        warninglayout = QVBoxLayout()
        errorwarninglayout = QHBoxLayout()
        
        #
        # Combo boxes
        #
        self.tiercombowidget = QComboBox()
        self.tiercombowidget.addItems([ "Prod", "Stage", "QA", "QA2", "Dev", "Dev2"])
        self.tiercombowidget.setPlaceholderText("Select a tier")
        self.tiercombowidget.setCurrentIndex(-1)
        self.tiercombowidget.currentTextChanged.connect(self.tier_changed)
        
        self.studycombowidget = QComboBox()
        self.studycombowidget.setPlaceholderText("Select a Study to see submissions")
        self.studycombowidget.setCurrentIndex(-1)
        self.studycombowidget.currentTextChanged.connect(self.study_changed)
        
        self.submissioncombowidget = QComboBox()
        self.submissioncombowidget.setPlaceholderText("Select a Submission to see details")
        self.submissioncombowidget.setCurrentIndex(-1)
        self.submissioncombowidget.currentTextChanged.connect(self.submission_reset)
        self.submissioncombowidget.currentTextChanged.connect(self.submission_raw_changed)
        self.submissioncombowidget.currentTextChanged.connect(self.submission_percentage_changed)
        #self.submissioncombowidget.currentTextChanged.connect(self.errorpie)
        self.submissioncombowidget.currentTextChanged.connect(self.error_warning_tables)
        self.submissioncombowidget.currentTextChanged.connect(self.full_error_tab)
        self.submissioncombowidget.currentTextChanged.connect(self.full_warning_tab)
        self.submissioncombowidget.currentTextChanged.connect(self.full_data_tab)
        
        
        #
        # Submission Table
        #
        self.submissiontablelabel = QLabel("Submissions")
        self.submissiontable = QTableView()
        self.submissiontable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.submissiontable.setAlternatingRowColors(True)
        #
        # Node Count bar charts
        #
        self.node_raw_widget = pg.PlotWidget()
        self.node_percentage_widget = pg.PlotWidget()
        
        barlayout.addWidget(self.node_raw_widget)
        barlayout.addWidget(self.node_percentage_widget)
        barwidget = QWidget()
        barwidget.setLayout(barlayout)
        
        #
        #  Error and warning tables
        #
        self.errorsummarylabel = QLabel("Error Summary")
        self.errorsummarytable = QTableView()
        self.errorsummarytable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.errorsummarytable.setAlternatingRowColors(True)
        self.warningsummarylabel = QLabel("Warning Summary")
        self.warningsummarytable = QTableView()
        self.warningsummarytable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.warningsummarytable.setAlternatingRowColors(True)
        errorlayout.addWidget(self.errorsummarylabel)
        errorlayout.addWidget(self.errorsummarytable)
        errorwidget = QWidget()
        errorwidget.setLayout(errorlayout)
   
        warninglayout.addWidget(self.warningsummarylabel)
        warninglayout.addWidget(self.warningsummarytable)
        warningwidget = QWidget()
        warningwidget.setLayout(warninglayout)
        
        errorwarninglayout.addWidget(errorwidget)
        errorwarninglayout.addWidget(warningwidget)
        errorwarningwidget = QWidget()
        errorwarningwidget.setLayout(errorwarninglayout)
        
        #
        # Full Error, warning, and submitted data tables
        #
        
        self.fullerrorlabel = QLabel("Error Details")
        self.fullerrortable = QTableView()
        self.fullerrortable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fullerrortable.setAlternatingRowColors(True)
        self.errordropdown = QComboBox()
        self.errordropdown.setPlaceholderText("Select an error for full details")
        self.errordropdown.setCurrentIndex(-1)
        self.errordropdown.currentTextChanged.connect(self.full_error_table)
        self.errorheaderlayout = QHBoxLayout()
        self.errorheaderlayout.addWidget(self.fullerrorlabel)
        self.errorheaderlayout.addWidget(self.errordropdown)
        self.errorheaderwidget = QWidget()
        self.errorheaderwidget.setLayout(self.errorheaderlayout)
        self.fullerrorlayout = QVBoxLayout()
        self.fullerrorlayout.addWidget(self.errorheaderwidget)
        self.fullerrorlayout.addWidget(self.fullerrortable)
        self.fullerrorwidget = QWidget()
        self.fullerrorwidget.setLayout(self.fullerrorlayout)
        
        
        self.fullwarninglabel = QLabel("Warning Details")
        self.fullwarningtable = QTableView()
        self.fullwarningtable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fullwarningtable.setAlternatingRowColors(True)
        self.warningdropdown = QComboBox()
        self.warningdropdown.setPlaceholderText("Select a warning for full details")
        self.warningdropdown.setCurrentIndex(-1)
        self.warningdropdown.currentTextChanged.connect(self.full_warning_table)
        self.warningheaderlayout = QHBoxLayout()
        self.warningheaderlayout.addWidget(self.fullwarninglabel)
        self.warningheaderlayout.addWidget(self.warningdropdown)
        self.warningheaderwidget = QWidget()
        self.warningheaderwidget.setLayout(self.warningheaderlayout)
        self.fullwarninglayout = QVBoxLayout()
        self.fullwarninglayout.addWidget(self.warningheaderwidget)
        self.fullwarninglayout.addWidget(self.fullwarningtable)
        self.fullwarningwidget = QWidget()
        self.fullwarningwidget.setLayout(self.fullwarninglayout)
        
        self.fulldatalabel = QLabel("Submitted Data Details")
        self.fulldatatable = QTableView()
        #self.fulldatatable = QTableWidget()
        self.fulldatatable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fulldatatable.setAlternatingRowColors(True)
        self.datadropdown = QComboBox()
        self.datadropdown.setPlaceholderText("Select a node to see data")
        self.datadropdown.setCurrentIndex(-1)
        self.datadropdown.currentTextChanged.connect(self.full_data_table)
        self.dataheaderlayout = QHBoxLayout()
        self.dataheaderlayout.addWidget(self.fulldatalabel)
        self.dataheaderlayout.addWidget(self.datadropdown)
        self.dataheaderwidget = QWidget()
        self.dataheaderwidget.setLayout(self.dataheaderlayout)
        self.fulldatalayout = QVBoxLayout()
        self.fulldatalayout.addWidget(self.dataheaderwidget)
        self.fulldatalayout.addWidget(self.fulldatatable)
        self.fulldatawidget = QWidget()
        self.fulldatawidget.setLayout(self.fulldatalayout)

        
        
        # Dropdown layous
        dropdownlayout.addWidget(self.tiercombowidget)
        dropdownlayout.addWidget(self.studycombowidget)
        dropdownlayout.addWidget(self.submissioncombowidget)
        dropdownwidget = QWidget()
        dropdownwidget.setLayout(dropdownlayout)
        
        #
        # Pie Charts
        #
        #self.errorpieseries = QPieSeries()
        #self.errorpiechart = QChart()
        #self.errorpieview = QChartView()
        
        #pielayout.addWidget(self.errorpieview)
        #piewidget = QWidget()
        #piewidget.setLayout(self.pielayout)
        
        #Overall Summary Tab layouy
        summarylayout.addWidget(dropdownwidget)
        summarylayout.addWidget(self.submissiontablelabel)
        summarylayout.addWidget(self.submissiontable)
        summarylayout.addWidget(barwidget)
        summarylayout.addWidget(errorwarningwidget)
        summarywidget = QWidget()
        summarywidget.setLayout(summarylayout)
        
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.West)
        tabpalette = tabs.palette()
        tabpalette.setColor(tabs.backgroundRole(), QColor.fromString(self.tab_color) )
        #tabs.setPalette(tabpalette)

        #tabs.addTab(dropdownwidget, "Summary")
        tabs.addTab(summarywidget, "Summary")
        tabs.addTab(self.fullerrorwidget, "Errors")
        tabs.addTab(self.fullwarningwidget, "Warnings")
        tabs.addTab(self.fulldatawidget, "Data")
        
        
        
            
        self.setCentralWidget(tabs)
        
        
    def tier_changed(self, t):
        #Reset everything
        self.theDataThing.fullReset()
        # Now go get stuff
        self.creds = dhAPICreds(t.lower())
        if self.creds['token'] is None and self.creds['url'] is not None:
            bummer = CustomDialog("Login Error", f"No API key for {t}")
            bummer.exec()
            self.tiercombowidget.setCurrentIndex(-1)
        elif self.creds['token'] is None and self.creds['url'] is None:
            bummer2 = CustomDialog("Login Error", f"No API key or URL for {t}")
            bummer2.exec
            self.tiercombowidget.setCurrentIndex(-1)
        else:
            #vars = {"status":["New", "In Progress", "Submitted", "Rejected", "Withdrawn", "Released"]}
            self.theDataThing.getStudyInfo(url=self.creds['url'], apitoken=self.creds['token'])
            self.studycombowidget.clear()
            self.studycombowidget.addItems(self.theDataThing.getStudyList())
            self.studycombowidget.setCurrentIndex(-1)


       
    def study_changed(self, abbrev):
        # Study level reset
        self.theDataThing.studyReset()
        self.submissioncombowidget.clear()
        self.model = SubmissionTableModel(pd.DataFrame())
        self.submissiontable.setModel(self.model)
        # Get new data
        vars = {"status": "All"}
        self.theDataThing.getSubmissionInfo(url=self.creds['url'], apitoken=self.creds['token'], variables=vars, abbrev=abbrev)
        df = self.theDataThing.getSubmissionDataFrame()
        #print(df)
        self.model = SubmissionTableModel(df)
        self.submissiontable.setModel(self.model)
        
        self.submissiontablelabel.clear()
        self.submissiontablelabel.setText(f"Submission for {abbrev}")
        self.submissioncombowidget.clear()
        self.submissioncombowidget.addItems(self.theDataThing.getSubmissionList())
        self.submissioncombowidget.setCurrentIndex(-1)


    def submission_reset(self, name):
        self.theDataThing.submissionReset()
            
    def submission_raw_changed(self, name):
        self.node_raw_widget.clear()
        self.node_raw_widget.setTitle(f"Raw node counts for {name}")
        self.node_raw_widget.setLabel("left", "Count")
        self.node_raw_widget.setLabel("bottom", "Node")
        
        graphdata_df = self.theDataThing.barChartCountData2(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        
        # This builds the array used to change the lables
        nodecount = 1
        categorydata = {}
        for node in graphdata_df['nodeName'].tolist():
            categorydata[nodecount] = node
            nodecount = nodecount + 1
        
        nodes = np.array(list(categorydata.keys()), dtype=float)
        newstate = np.array(graphdata_df['new'].tolist())
        errorstate = np.array(graphdata_df['error'].tolist())
        warnstate = np.array(graphdata_df['warning'].tolist())
        passstate = np.array(graphdata_df['passed'].tolist())
        
        width = .5
        newbar = pg.BarGraphItem(x=nodes, height=newstate, width=width, brush=self.sub_blue, name="New")
        errorbar = pg.BarGraphItem(x=nodes, height=errorstate, width= width, brush=self.sub_red, name="Error")
        warnbar = pg.BarGraphItem(x=nodes, height=warnstate, width= width, brush=self.sub_yellow, name="Warning")
        passbar = pg.BarGraphItem(x=nodes, height=passstate, width= width, brush=self.sub_green, name="Passed")
        
        self.node_raw_widget.addItem(newbar)
        self.node_raw_widget.addItem(errorbar)
        self.node_raw_widget.addItem(warnbar)
        self.node_raw_widget.addItem(passbar)
        
        ax = self.node_raw_widget.getAxis("bottom")
        ax.setTicks([list(categorydata.items())])
    
    
    def submission_percentage_changed(self, name):
        self.node_percentage_widget.clear()
        self.node_percentage_widget.setTitle(f"Percentage counts for {name}")
        self.node_percentage_widget.setLabel("left", "Count")
        self.node_percentage_widget.setLabel("bottom", "Node")
        
        graphdata_df = self.theDataThing.barChartCountData2(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name, percentage=True)
                
        nodecount = 1
        categorydata = {}
        for node in graphdata_df['nodeName'].tolist():
            categorydata[nodecount] = node
            nodecount = nodecount + 1
        
        nodes = np.array(list(categorydata.keys()), dtype=float)
        newstate = np.array(graphdata_df['new'].tolist())
        errorstate = np.array(graphdata_df['error'].tolist())
        warnstate = np.array(graphdata_df['warning'].tolist())
        passstate = np.array(graphdata_df['passed'].tolist())
        
        width = .5
        newbar = pg.BarGraphItem(x=nodes, height=newstate, width=width, brush=self.sub_blue, name="New")
        errorbar = pg.BarGraphItem(x=nodes, height=errorstate, width= width, brush=self.sub_red, name="Error")
        warnbar = pg.BarGraphItem(x=nodes, height=warnstate, width= width, brush=self.sub_yellow, name="Warning")
        passbar = pg.BarGraphItem(x=nodes, height=passstate, width= width, brush=self.sub_green, name="Passed")
        
        self.node_percentage_widget.addItem(newbar)
        self.node_percentage_widget.addItem(errorbar)
        self.node_percentage_widget.addItem(warnbar)
        self.node_percentage_widget.addItem(passbar)
        
        ax = self.node_percentage_widget.getAxis("bottom")
        ax.setTicks([list(categorydata.items())])
    
    
    def errorpie(self, name):
        print("ErrorPieChart")
        errors = self.theDataThing.validationErrorData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        print(f"Errors:\n{errors}")
        sliceslist = []
        keylist = []
        for slicelabel, slicevalue in errors.items():
            keylist.append(slicelabel)
            sliceslist.append(int(slicevalue))
        
        errorpiechart = PieCanvas(pieslices=sliceslist, pielabels=keylist)
        self.pielayout.addWidget(errorpiechart)
        
        #for error, count in errors.items():
        #    self.errorpieseries.append(error, int(count))
       # 
       # #self.slice = self.errorpieseries.slices()
       # #self.slice.setLabelVisible()
       # 
       # print(f"Error Pie Series {self.errorpieseries}")
       # self.errorpiechart.addSeries(self.errorpieseries)
       # self.errorpiechart.setTitle("Error Summary")
       # self.errorpieview.setChart(self.errorpiechart)
       # self.errorpieview.setRenderHint


    def error_warning_tables(self, name):
        #Delete all the old stuff
        self.errormodel = SubmissionTableModel(pd.DataFrame())
        self.warningmodel = SubmissionTableModel(pd.DataFrame())
        self.errorsummarytable.setModel(self.errormodel)
        self.warningsummarytable.setModel(self.warningmodel)
        #Add new data
        error_df = self.theDataThing.validationErrorData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        warning_df = self.theDataThing.validationWarningData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        if error_df is not None:
            self.errormodel = SubmissionTableModel(error_df)
            self.errorsummarytable.setModel(self.errormodel)
        if warning_df is not None:
            self.warningmodel = SubmissionTableModel(warning_df)
            self.warningsummarytable.setModel(self.warningmodel)
            
    
    def full_error_tab(self, name):
        self.theDataThing.fullValidationErrorData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        self.errordropdown.addItems(self.theDataThing.errorDropDownValues())
        
    def full_warning_tab(self,name):
        self.theDataThing.fullValidationWarningData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        self.warningdropdown.addItems(self.theDataThing.warningDropDownValues())
        
    def full_error_table(self, name):
        fullerror_df = self.theDataThing.fullValidationErrorTableData(name)
        self.fullerrormodel = SubmissionTableModel(fullerror_df)
        self.fullerrortable.setModel(self.fullerrormodel)
    
    def full_warning_table(self, name):
        fullwarning_df = self.theDataThing.fullValidationWarningTableData(name)
        self.fullwarningmodel = SubmissionTableModel(fullwarning_df)
        self.fullwarningtable.setModel(self.fullwarningmodel)
        
    def full_data_tab(self, name):
        self.datadropdown.addItems(self.theDataThing.dataNodeDropDown(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name))
    
    
    def full_data_table(self, name):
        data_df = self.theDataThing.fullDataNodeTableData(url=self.creds['url'], apitoken=self.creds['token'], submissionname=self.submissioncombowidget.currentText(), nodename=name)
        if data_df is not None:
            self.fulldatamodel = SubmissionTableModel(data_df)
            self.fulldatatable.setModel(self.fulldatamodel)
            
    
    def submission_reset(self, name):
        #Run when the submisison is changed
        self.resetmodel = SubmissionTableModel(pd.DataFrame())
        
        ##self.fulldatamodel = SubmissionTableModel(pd.DataFrame())
        self.fulldatatable.setModel(self.resetmodel)
        
        #self.fullwarningmodel = SubmissionTableModel(pd.DataFrame())
        self.fullwarningtable.setModel(self.resetmodel)
        
        #self.fullerrormodel = SubmissionTableModel(pd.DataFrame())
        self.fullerrortable.setModel(self.resetmodel)
        
        #self.errormodel = SubmissionTableModel(pd.DataFrame())
        #self.warningmodel = SubmissionTableModel(pd.DataFrame())
        self.errorsummarytable.setModel(self.resetmodel)
        self.warningsummarytable.setModel(self.resetmodel)



app = QApplication([])
window = MainWindow()
window.resize(QSize(1500,700))
window.show()
app.exec()
