from PyQt6.QtWidgets import QApplication,  QMainWindow,  QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QListWidget
from PyQt6.QtCore import QSize, QStandardPaths
import yaml

import os
from pathlib import Path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Data Submission Data File Upload")
        self.configFile = None
        self.cliBinary = None
        self.clipboard = QApplication.clipboard()

        #
        #  Layouts
        #
        mainLayout = QVBoxLayout()
        step1Layout = QHBoxLayout()
        step2Layout = QHBoxLayout()
        launchCloseLayout = QHBoxLayout()
        
        
        self.step1label = QLabel("Step 1: Select the configuration file")
        self.fileDialogButton = QPushButton("Select the configuration file")
        self.fileDialogButton.clicked.connect(self.launchFileDialog)
        step1Layout.addWidget(self.step1label)
        step1Layout.addWidget(self.fileDialogButton)
        step1widget = QWidget()
        step1widget.setLayout(step1Layout)
        
        configLayout = QVBoxLayout()
        self.configFileLabel = QLabel("Configuration file:")
        self.dataDirLabel = QLabel("Data directory:")
        self.submissionUUIDLabel = QLabel("Submission ID:")
        self.typeLabel = QLabel("Submission Type:")
        self.retriesLabel = QLabel("Number of retries:")
        self.overwriteLabel = QLabel("File overwrite status:")
        self.dryrunLabel = QLabel("Dry run status:")
        
        configLayout.addWidget(self.configFileLabel)
        configLayout.addWidget(self.dataDirLabel)
        configLayout.addWidget(self.submissionUUIDLabel)
        configLayout.addWidget(self.typeLabel)
        configLayout.addWidget(self.retriesLabel)
        configLayout.addWidget(self.overwriteLabel)
        configLayout.addWidget(self.dryrunLabel)
        
        configInfo = QWidget()
        configInfo.setLayout(configLayout)
        
        self.step2Label = QLabel("Step 2: Select the CLI Upload Tool Binary (uploader.exe)")
        self.cliDialogButton = QPushButton("Select the binary")
        self.cliDialogButton.clicked.connect(self.launchCLIDialog)
        step2Layout.addWidget(self.step2Label)
        step2Layout.addWidget(self.cliDialogButton)
        step2Widget = QWidget()
        step2Widget.setLayout(step2Layout)
        self.cliInfo = QLabel("Upload Tool:")
        
        self.launchButton = QPushButton("Copy the upload command to clipboard")
        self.exitButton = QPushButton("Exit")
        self.launchButton.clicked.connect(self.startUpload)
        self.exitButton.clicked.connect(self.close)
        self.commandLine = QLabel("")
        launchCloseLayout.addWidget(self.launchButton)
        launchCloseLayout.addWidget(self.exitButton)
        buttonwidget =QWidget()
        buttonwidget.setLayout((launchCloseLayout))
        
        mainWidget = QWidget()
        mainLayout.addWidget(step1widget)
        mainLayout.addWidget(configInfo)
        mainLayout.addWidget(step2Widget)
        mainLayout.addWidget(self.cliInfo)
        mainLayout.addWidget(buttonwidget)
        mainLayout.addWidget(self.commandLine)
        
        mainWidget.setLayout(mainLayout)
        
        
        
        self.setCentralWidget(mainWidget)
    
    def parseConfig(self, yamlfile):
        with open(yamlfile) as f:
                yamljson = yaml.safe_load(f)
        return yamljson['Config']
    
    
    def launchFileDialog(self):
        configDialog = QFileDialog(self)
        configDialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        configDialog.setViewMode(QFileDialog.ViewMode.Detail)
        configDialog.setDirectory(os.path.expanduser("~"))
        if configDialog.exec():
            fileNames = configDialog.selectedFiles()
            self.configFile = str(Path(fileNames[0]))
            configjson = self.parseConfig(self.configFile)
            self.configFileLabel.setText(f"Configuration file: {str(Path(fileNames[0]))}")
            self.dataDirLabel.setText(f"Data directory: {configjson['data']}")
            self.submissionUUIDLabel
            self.typeLabel.setText(f"Submission Type: {configjson['type']}")
            self.retriesLabel.setText(f"Number of retries: {configjson['retries']}")
            self.overwriteLabel.setText(f"File overwrite status: {configjson['overwrite']}")
            self.dryrunLabel.setText(f"Dry run status: {configjson['dryrun']}")
    
    
    def launchCLIDialog(self):
        cliDialog = QFileDialog(self)
        cliDialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        cliDialog.setViewMode(QFileDialog.ViewMode.Detail)
        cliDialog.setDirectory(os.path.expanduser("~"))
        if cliDialog.exec():
            fileNames = cliDialog.selectedFiles()
            self.cliBinary = str(Path(fileNames[0]))
            self.cliInfo.setText(f"Upload Tool: {self.cliBinary}")
            
    def startUpload(self):
        uploadcommand = f"{self.cliBinary} --config {self.configFile}"
        self.commandLine.setText(uploadcommand)
        self.clipboard.setText(uploadcommand)


app = QApplication([])
window = MainWindow()
window.resize(QSize(1500,700))
window.show()
app.exec()