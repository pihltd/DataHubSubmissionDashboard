from PyQt6.QtWidgets import QApplication,  QMainWindow, QTabWidget, QVBoxLayout, QComboBox, QHBoxLayout, QWidget, QTableView, QLabel
from PyQt6.QtCore import QSize
from PyQt6.QtCharts import QPieSeries, QPieSlice
import pyqtgraph as pg

import pandas as pd
import numpy as np

from src.qtDHFunctions import dhAPICreds
from src.qtSubclasses import CustomDialog, SubmissionTableModel
from src.qtData import SubmissionData

from layout_color_widget import Color

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.submission_df = pd.DataFrame()
        self.theDataThing = SubmissionData()
        
        self.creds = None
        
        self.sub_blue = '#3498DB' 
        self.sub_red =  '#E74C3C'
        self.sub_yellow = '#F4D03F'
        self.sub_green =  '#16A085'
        
        
        self.setWindowTitle("CRDC Dashboard")
        
        #
        #  Layouts
        #
        summarylayout = QVBoxLayout()
        dropdownlayout = QHBoxLayout()
        barlayout = QHBoxLayout()
        
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
        self.submissioncombowidget.currentTextChanged.connect(self.submission_changed)
        self.submissioncombowidget.currentTextChanged.connect(self.submission_stacked_changed)
        
        #
        # Submission Table
        #
        self.submissiontablelabel = QLabel("Submissions")
        self.submissiontable = QTableView()
        
        #
        # Node Count bar charts
        #
        self.node_count_widget = pg.PlotWidget()
        self.node_stacked_widget = pg.PlotWidget()
        
        barlayout.addWidget(self.node_count_widget)
        barlayout.addWidget(self.node_stacked_widget)
        barwidget = QWidget()
        barwidget.setLayout(barlayout)
        
        
        # Dropdown layous
        dropdownlayout.addWidget(self.tiercombowidget)
        dropdownlayout.addWidget(self.studycombowidget)
        dropdownlayout.addWidget(self.submissioncombowidget)
        dropdownwidget = QWidget()
        dropdownwidget.setLayout(dropdownlayout)
        
        #Overall Summary Tab layouy
        summarylayout.addWidget(dropdownwidget)
        summarylayout.addWidget(self.submissiontablelabel)
        summarylayout.addWidget(self.submissiontable)
        summarylayout.addWidget(barwidget)
        summarywidget = QWidget()
        summarywidget.setLayout(summarylayout)
        
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.West)

        #tabs.addTab(dropdownwidget, "Summary")
        tabs.addTab(summarywidget, "Summary")
        
        
        
            
        self.setCentralWidget(tabs)
        
        
    def tier_changed(self, t):
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

    
    def submission_changed(self, name):
        #self.theDataThing.getErrorPieChartInfo(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        # Set up a few things
        self.node_count_widget.setTitle(f"Node counts for {name}")
        self.node_count_widget.setLabel("left", "Count")
        self.node_count_widget.setLabel("bottom", "Node")
        nodenamedict, totalcountlist = self.theDataThing.barChartCountData(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        nodes = np.array(list(nodenamedict.keys()), dtype=float)
        width = .25
        
        bar = pg.BarGraphItem(
            x = nodes,
            height = totalcountlist,
            width = width
        )
        
        self.node_count_widget.addItem(bar)
        ax = self.node_count_widget.getAxis("bottom")
        ax.setTicks([list(nodenamedict.items())])
        
    def submission_stacked_changed(self, name):
        self.node_stacked_widget.setTitle(f"Node counts for {name}")
        self.node_stacked_widget.setLabel("left", "Count")
        self.node_stacked_widget.setLabel("bottom", "Node")
        
        graphdata_df = self.theDataThing.barChartCountData2(url=self.creds['url'], apitoken=self.creds['token'],submissionname=name)
        
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
        
        self.node_stacked_widget.addItem(newbar)
        self.node_stacked_widget.addItem(errorbar)
        self.node_stacked_widget.addItem(warnbar)
        self.node_stacked_widget.addItem(passbar)
        
        ax = self.node_stacked_widget.getAxis("bottom")
        ax.setTicks([list(categorydata.items())])

        
app = QApplication([])
window = MainWindow()
#window.setMinimumSize(QSize(1500,700))
window.resize(QSize(1500,700))
window.show()
app.exec()
