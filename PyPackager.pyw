import os
import sys
import subprocess
import threading
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import tkinter as tk
from PyQt5 import QtCore, QtGui, QtWidgets
from random import randrange
from shutil import make_archive, rmtree, copyfile

root = tk.Tk()
root.withdraw()

class Ui_MainWindow(object):
    def build(self):
        self.createinstaller.setEnabled(False)
        self.listWidget.clear()
        version = self.versioninput.text()
        name = self.nameinput.text()

        os.chdir(self.dirname)
        deletetempicon = []
        
        icon = self.iconinput.text().strip()
        if icon == '':
            if os.path.exists('icon.ico'): icon = 'icon.ico'
            if os.path.exists('ico.ico'): icon = 'ico.ico'
            if os.path.exists('favicon.ico'): icon = 'favicon.ico'
            if os.path.exists(f'{name}.ico'): icon = f'{name}.ico'
            if os.path.exists(f'{name} {version}.ico'): icon = f'{name} {version}.ico'
            if os.path.exists(f'{name} v{version}.ico'): icon = f'{name} v{version}.ico'
        if icon != '':
            tempicon = f'icon-temp-{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}.ico'
            copyfile(icon, os.path.join(self.dirname, tempicon))
            icon = os.path.join(self.dirname, tempicon)
            deletetempicon.append(icon)

        window = self.windowinput.text().strip()
        if window == '':
            if os.path.exists('icon.png'): window = 'icon.png'
            if os.path.exists('ico.png'): window = 'ico.png'
            if os.path.exists('favicon.png'): window = 'favicon.png'
            if os.path.exists(f'{name}.png'): window = f'{name}.png'
            if os.path.exists(f'{name} {version}.png'): window = f'{name} {version}.png'
            if os.path.exists(f'{name} v{version}.png'): window = f'{name} v{version}.png'

        if window == '' and icon != '':
            self.statusbar.showMessage('Converting icon...')
            tempicon = f'window-icon-temp-{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}.png'
            process = subprocess.Popen([os.path.join(os.path.dirname(sys.argv[0]), 'ffmpeg.exe'), '-i', icon, '-vf', 'scale=100:-1', tempicon], stdout=subprocess.PIPE)
            for line in iter(process.stdout.readline, b''):
                self.listWidget.addItem(line.decode("utf-8").strip())
            deletetempicon.append(tempicon)
            window = os.path.join(self.dirname, tempicon)
        elif window != '':
            tempicon = f'window-icon-temp-{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}.png'
            process = subprocess.Popen([os.path.join(os.path.dirname(sys.argv[0]), 'ffmpeg.exe'), '-i', window, '-vf', 'scale=100:-1', tempicon], stdout=subprocess.PIPE)
            for line in iter(process.stdout.readline, b''):
                self.listWidget.addItem(line.decode("utf-8").strip())
            deletetempicon.append(tempicon)
            window = os.path.join(self.dirname, tempicon)

        self.statusbar.showMessage('Compiling...')
        command = ['cxfreeze']
        if icon != '': command.append(f'--icon={icon}')
        if self.dependentfiles != []: command.append(f'--include-files={",".join([elem for elem in self.dependentfiles])}')
        command.append(f'--target-name=start.exe')
        if self.enableconsolecheck.isChecked():
            command.append(f'--base-name=Console')
        else:
            command.append(f'--base-name=Win32GUI')

        newdir = f'build_temp-{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}'
        command.append(f'--target-dir={newdir}')

        command.append(self.inputfile)

        try: process = subprocess.Popen(command, stdout=subprocess.PIPE)
        except FileNotFoundError:
            sys.exit(-1)

        for line in iter(process.stdout.readline, b''):
            self.listWidget.addItem(line.decode("utf-8").strip())

        if self.createzipcheck.isChecked():
            self.statusbar.showMessage('Creating portable zip...')
            zipname = f'{name} v{version}p (x64)'
            while True:
                if os.path.exists(zipname):
                    zipname = zipname+' (2)'
                else:
                    break
            make_archive(zipname, 'zip', newdir)

        self.statusbar.showMessage('Building installer...')
        os.chdir(newdir)
        tempfilename = f'archive-temp-{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}{str(randrange(10))}.txt'
        f = open(tempfilename, "w")
        replacevals = lambda x: x.replace('{name}', name).replace('{version}', version).replace('{ver}', version)
        archive_comment = [';The comment below contains SFX script commands\n', f'Path={replacevals(self.extractionpathinput.text())}', 'SavePath']
        windowtitle = self.windowtitleinput.text().strip()
        windowtext = self.windowtextinput.toPlainText().strip()
        if windowtitle != '': archive_comment.append(f'Title={replacevals(windowtitle)}')
        if windowtext != '': archive_comment.append('Text\n{\n'+replacevals(windowtext)+'\n}')

        for item in self.setupfiles:
            archive_comment.append(f'Setup={item}')

        if self.desktopshortcutcheck.isChecked(): archive_comment.append(f'Shortcut=D, start.exe, \\, {name} v{version}, {name} v{version}, ')
        if self.startmenushortcutcheck.isChecked(): archive_comment.append(f'Shortcut=P, start.exe, \\, {name} v{version}, {name} v{version}, ')
        if self.startupshortcutcheck.isChecked(): archive_comment.append(f'Shortcut=T, start.exe, \\, {name} v{version}, {name} v{version}, ')

        f.write('\n'.join(archive_comment))
        f.close()
        if icon == '': iconcmd = ''
        else: iconcmd = f'-iicon"{icon}"'
        if window == '': wiconcmd = ''
        else: wiconcmd = f'-iimg"{window}"'

        installer_name = f'{name} v{version} Installer (x64)'

        while True:
            if os.path.exists(os.path.join(self.dirname, f'{installer_name}.exe')):
                installer_name = installer_name+' (2)'
            else: break

        installer_command = f'"C:\\Program Files\\WinRAR\\WinRAR.exe" a -r -sfx {iconcmd} {wiconcmd} -z"{tempfilename}" "{installer_name}" "'+'" "'.join(os.listdir())+'"'
        self.statusbar.showMessage('Creating SFX archive...')

        p = subprocess.Popen(installer_command)
        p.wait()

        self.statusbar.showMessage('Clearing temp files...')
        os.chdir(self.dirname)
        os.rename(os.path.join(self.dirname, newdir, f"{installer_name}.exe"), os.path.join(self.dirname, f"{installer_name}.exe"))
        rmtree(newdir)
        for i in deletetempicon:
            os.remove(i)

        self.statusbar.showMessage('Complete.')
        #if messagebox.askokcancel('Complete', 'PyPackager is now complete. Would you like to open the file location?'):
        #    subprocess.Popen(f'explorer /select,"{os.path.join(self.dirname, f"{installer_name}.exe")}"')
        #self.statusbar.clearMessage()
        self.createinstaller.setEnabled(True)

    def dependentfileadd(self):
        addinput = self.adddependentfileinput.text().strip()
        if addinput == '': messagebox.showerror('Input Error', 'There is nothing to add.')
        elif addinput in self.dependentfiles: messagebox.showerror('Input Error', f'"{addinput}" is already in the dependent files/folders list.')
        else:
            self.dependentfiles.append(addinput)
            self.dependentfiles.sort()
            self.dependentfileslist.clear()
            self.adddependentfileinput.clear()
            self.dependentfileslist.addItems(self.dependentfiles)

    def dependentfiledel(self):
        if len(self.dependentfiles) != 0:
            currow = self.dependentfileslist.currentRow()
            self.dependentfiles.remove(self.dependentfiles[currow])
            self.dependentfileslist.clear()
            self.dependentfileslist.addItems(self.dependentfiles)
            self.dependentfileslist.setCurrentRow(currow)
        else:
            messagebox.showerror('Error', 'There is nothing to delete.')

    def runbuild(self):
        t = threading.Thread(target=self.build)
        t.daemon = True
        t.start()

    def refreshit(self):
        inputfile = str(askopenfilename(title='Open a python file', filetypes= [("Python", "*.py *.pyw"), ("UI", "*.ui")])).replace('/', '\\').strip()
        if os.path.exists(inputfile):
            self.inputfile = inputfile
            self.setconnections2()

    def dependentfileclear(self):
        self.dependentfileslist.clear()
        self.dependentfiles = []

    def finishedfileclear(self):
        self.runonfinishedlist.clear()
        self.setupfiles = []

    def finishedfileadd(self):
        addinput = self.addfinishedinput.text().strip()
        if addinput == '': messagebox.showerror('Input Error', 'There is nothing to add.')
        elif addinput in self.setupfiles: messagebox.showerror('Input Error', f'"{addinput}" is already in the setup files/folders list.')
        else:
            self.setupfiles.append(addinput)
            self.setupfiles.sort()
            self.runonfinishedlist.clear()
            self.addfinishedinput.clear()
            self.runonfinishedlist.addItems(self.setupfiles)

    def finishedfiledel(self):
        if len(self.setupfiles) != 0:
            currow = self.runonfinishedlist.currentRow()
            self.setupfiles.remove(self.setupfiles[currow])
            self.runonfinishedlist.clear()
            self.runonfinishedlist.addItems(self.setupfiles)
            self.runonfinishedlist.setCurrentRow(currow)
        else:
            messagebox.showerror('Error', 'There is nothing to delete.')

    def chooseicofile(self):
        icon = str(askopenfilename(title='Open an ico file', filetypes= [("Icon", "*.ico")])).replace('/', '\\').strip()
        if not icon in ('', 'None'):
            self.iconinput.setText(icon)

    def choosepngfile(self):
        icon = str(askopenfilename(title='Open a png file', filetypes= [("Image", "*.png *.jpg *.bmp *.ico")])).replace('/', '\\').strip()
        if not icon in ('', 'None'):
            self.windowinput.setText(icon)

    def setconnections2(self):
        self.dependentfiles = []
        self.setupfiles = []
        self.dependentfileslist.clear()
        self.runonfinishedlist.clear()
        self.addfinishedbutton.clicked.connect(self.finishedfileadd)
        self.removefinishedbutton.clicked.connect(self.finishedfiledel)
        self.clearfinishedbutton.clicked.connect(self.finishedfileclear)
        self.inputfilebrowse_2.clicked.connect(self.chooseicofile)
        self.inputfilebrowse_3.clicked.connect(self.choosepngfile)
        self.enableconsolecheck.setChecked(not os.path.splitext(self.inputfile)[1] == '.pyw')
        self.inputfileinput.setText(self.inputfile)
        self.nameinput.setText(os.path.splitext(os.path.basename(self.inputfile))[0])
        self.dirname = os.path.dirname(self.inputfile)
        self.dependentfiles = os.listdir(self.dirname)
        self.dependentfiles.remove(os.path.basename(self.inputfile))
        self.dependentfileslist.addItems(self.dependentfiles)
        self.addidependentbutton.clicked.connect(self.dependentfileadd)
        self.createinstaller.clicked.connect(self.runbuild)
        self.inputfilebrowse.clicked.connect(self.refreshit)
        self.removedependentbutton.clicked.connect(self.dependentfiledel)
        self.cleardependentbutton.clicked.connect(self.dependentfileclear)
        MainWindow.show()


    def setconnections(self):
        MainWindow.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(sys.argv[0]), 'icon.ico')))
        if not sys.platform.lower().startswith('win'):
            messagebox.showerror('OS Error', '"PyPackager" only supports Windows.')
            sys.exit()
        if not os.path.exists("C:\\Program Files\\WinRAR\\WinRAR.exe"):
            messagebox.showerror('WinRAR not found', 'This application relies heavily on WinRAR and cxfreeze (python 3). Please install WinRAR to C:\\Program Files and try again.')
            sys.exit()
        if len(sys.argv) == 2:
            if os.path.exists(sys.argv[1]):
                if os.path.splitext(sys.argv[1])[1].lower() in ('.py', '.pyw', '.ui'):
                    self.inputfile = sys.argv[1]
                else: self.inputfile = str(askopenfilename(title='Open a python file', filetypes= [("Python", "*.py *.pyw"), ("UI", "*.ui")])).replace('/', '\\').strip()
            else: self.inputfile = str(askopenfilename(title='Open a python file', filetypes= [("Python", "*.py *.pyw"), ("UI", "*.ui")])).replace('/', '\\').strip()
        else: self.inputfile = str(askopenfilename(title='Open a python file', filetypes= [("Python", "*.py *.pyw"), ("UI", "*.ui")])).replace('/', '\\').strip()
        if self.inputfile in ('', 'None'):
            sys.exit()
        filetype = os.path.splitext(self.inputfile)[1].lower()
        if filetype == '.ui':
            filename = os.path.splitext(self.inputfile)[0]
            while True:
                if os.path.exists(filename+'.pyw'):
                    filename = filename + ' (2)'
                else:
                    break
            os.system(f'pyuic5 -x "{self.inputfile}" -o "{filename}.pyw"')
            sys.exit()

        else: self.setconnections2()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(294, 382)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(10, 311, 61, 16))
        self.label_6.setObjectName("label_6")
        self.inputfilebrowse = QtWidgets.QPushButton(self.centralwidget)
        self.inputfilebrowse.setGeometry(QtCore.QRect(260, 309, 31, 22))
        self.inputfilebrowse.setObjectName("inputfilebrowse")
        self.inputfileinput = QtWidgets.QLineEdit(self.centralwidget)
        self.inputfileinput.setGeometry(QtCore.QRect(68, 310, 191, 20))
        self.inputfileinput.setObjectName("inputfileinput")
        self.createinstaller = QtWidgets.QPushButton(self.centralwidget)
        self.createinstaller.setGeometry(QtCore.QRect(5, 337, 287, 23))
        self.createinstaller.setObjectName("createinstaller")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(5, 10, 287, 281))
        self.tabWidget.setMovable(True)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.removedependentbutton = QtWidgets.QPushButton(self.tab)
        self.removedependentbutton.setGeometry(QtCore.QRect(170, 180, 51, 22))
        self.removedependentbutton.setObjectName("removedependentbutton")
        self.nameinput = QtWidgets.QLineEdit(self.tab)
        self.nameinput.setGeometry(QtCore.QRect(100, 20, 171, 20))
        self.nameinput.setObjectName("nameinput")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(10, 22, 47, 16))
        self.label_3.setObjectName("label_3")
        self.dependentfileslist = QtWidgets.QListWidget(self.tab)
        self.dependentfileslist.setGeometry(QtCore.QRect(10, 100, 261, 79))
        self.dependentfileslist.setObjectName("dependentfileslist")
        self.addidependentbutton = QtWidgets.QPushButton(self.tab)
        self.addidependentbutton.setGeometry(QtCore.QRect(120, 180, 51, 22))
        self.addidependentbutton.setObjectName("addidependentbutton")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(10, 45, 47, 16))
        self.label_2.setObjectName("label_2")
        self.versioninput = QtWidgets.QLineEdit(self.tab)
        self.versioninput.setGeometry(QtCore.QRect(100, 44, 171, 20))
        self.versioninput.setObjectName("versioninput")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 80, 151, 16))
        self.label.setObjectName("label")
        self.adddependentfileinput = QtWidgets.QLineEdit(self.tab)
        self.adddependentfileinput.setGeometry(QtCore.QRect(10, 181, 108, 20))
        self.adddependentfileinput.setObjectName("adddependentfileinput")
        self.cleardependentbutton = QtWidgets.QPushButton(self.tab)
        self.cleardependentbutton.setGeometry(QtCore.QRect(220, 180, 51, 22))
        self.cleardependentbutton.setObjectName("cleardependentbutton")
        self.createzipcheck = QtWidgets.QCheckBox(self.tab)
        self.createzipcheck.setGeometry(QtCore.QRect(10, 220, 131, 17))
        self.createzipcheck.setObjectName("createzipcheck")
        self.enableconsolecheck = QtWidgets.QCheckBox(self.tab)
        self.enableconsolecheck.setGeometry(QtCore.QRect(170, 220, 131, 17))
        self.enableconsolecheck.setObjectName("enableconsolecheck")
        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.startupshortcutcheck = QtWidgets.QCheckBox(self.tab_3)
        self.startupshortcutcheck.setGeometry(QtCore.QRect(160, 200, 131, 17))
        self.startupshortcutcheck.setObjectName("startupshortcutcheck")
        self.desktopshortcutcheck = QtWidgets.QCheckBox(self.tab_3)
        self.desktopshortcutcheck.setGeometry(QtCore.QRect(10, 200, 141, 17))
        self.desktopshortcutcheck.setChecked(True)
        self.desktopshortcutcheck.setObjectName("desktopshortcutcheck")
        self.startmenushortcutcheck = QtWidgets.QCheckBox(self.tab_3)
        self.startmenushortcutcheck.setGeometry(QtCore.QRect(10, 220, 171, 17))
        self.startmenushortcutcheck.setChecked(True)
        self.startmenushortcutcheck.setObjectName("startmenushortcutcheck")
        self.extractionpathinput = QtWidgets.QLineEdit(self.tab_3)
        self.extractionpathinput.setGeometry(QtCore.QRect(99, 20, 171, 20))
        self.extractionpathinput.setObjectName("extractionpathinput")
        self.label_10 = QtWidgets.QLabel(self.tab_3)
        self.label_10.setGeometry(QtCore.QRect(9, 22, 81, 16))
        self.label_10.setObjectName("label_10")
        self.runonfinishedlist = QtWidgets.QListWidget(self.tab_3)
        self.runonfinishedlist.setGeometry(QtCore.QRect(10, 80, 261, 69))
        self.runonfinishedlist.setObjectName("runonfinishedlist")
        self.addfinishedinput = QtWidgets.QLineEdit(self.tab_3)
        self.addfinishedinput.setGeometry(QtCore.QRect(10, 151, 108, 20))
        self.addfinishedinput.setObjectName("addfinishedinput")
        self.clearfinishedbutton = QtWidgets.QPushButton(self.tab_3)
        self.clearfinishedbutton.setGeometry(QtCore.QRect(220, 150, 51, 22))
        self.clearfinishedbutton.setObjectName("clearfinishedbutton")
        self.addfinishedbutton = QtWidgets.QPushButton(self.tab_3)
        self.addfinishedbutton.setGeometry(QtCore.QRect(120, 150, 51, 22))
        self.addfinishedbutton.setObjectName("addfinishedbutton")
        self.removefinishedbutton = QtWidgets.QPushButton(self.tab_3)
        self.removefinishedbutton.setGeometry(QtCore.QRect(170, 150, 51, 22))
        self.removefinishedbutton.setObjectName("removefinishedbutton")
        self.label_11 = QtWidgets.QLabel(self.tab_3)
        self.label_11.setGeometry(QtCore.QRect(10, 60, 231, 16))
        self.label_11.setObjectName("label_11")
        self.line = QtWidgets.QFrame(self.tab_3)
        self.line.setGeometry(QtCore.QRect(10, 180, 261, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_5 = QtWidgets.QLabel(self.tab_2)
        self.label_5.setGeometry(QtCore.QRect(10, 45, 71, 16))
        self.label_5.setObjectName("label_5")
        self.iconinput = QtWidgets.QLineEdit(self.tab_2)
        self.iconinput.setGeometry(QtCore.QRect(88, 20, 151, 20))
        self.iconinput.setObjectName("iconinput")
        self.windowinput = QtWidgets.QLineEdit(self.tab_2)
        self.windowinput.setGeometry(QtCore.QRect(88, 43, 151, 20))
        self.windowinput.setObjectName("windowinput")
        self.label_4 = QtWidgets.QLabel(self.tab_2)
        self.label_4.setGeometry(QtCore.QRect(10, 22, 47, 16))
        self.label_4.setObjectName("label_4")
        self.label_7 = QtWidgets.QLabel(self.tab_2)
        self.label_7.setGeometry(QtCore.QRect(10, 115, 71, 16))
        self.label_7.setObjectName("label_7")
        self.windowtitleinput = QtWidgets.QLineEdit(self.tab_2)
        self.windowtitleinput.setGeometry(QtCore.QRect(10, 90, 261, 20))
        self.windowtitleinput.setObjectName("windowtitleinput")
        self.windowtextinput = QtWidgets.QTextEdit(self.tab_2)
        self.windowtextinput.setGeometry(QtCore.QRect(10, 135, 261, 101))
        self.windowtextinput.setObjectName("windowtextinput")
        self.label_8 = QtWidgets.QLabel(self.tab_2)
        self.label_8.setGeometry(QtCore.QRect(10, 70, 71, 16))
        self.label_8.setObjectName("label_8")
        self.inputfilebrowse_2 = QtWidgets.QPushButton(self.tab_2)
        self.inputfilebrowse_2.setGeometry(QtCore.QRect(240, 19, 31, 22))
        self.inputfilebrowse_2.setObjectName("inputfilebrowse_2")
        self.inputfilebrowse_3 = QtWidgets.QPushButton(self.tab_2)
        self.inputfilebrowse_3.setGeometry(QtCore.QRect(240, 42, 31, 22))
        self.inputfilebrowse_3.setObjectName("inputfilebrowse_3")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.listWidget = QtWidgets.QListWidget(self.tab_4)
        self.listWidget.setGeometry(QtCore.QRect(0, 2, 281, 251))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.listWidget.setFont(font)
        self.listWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        self.tabWidget.addTab(self.tab_4, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PyPackager"))
        self.label_6.setText(_translate("MainWindow", "Input File:"))
        self.inputfilebrowse.setText(_translate("MainWindow", "..."))
        self.createinstaller.setText(_translate("MainWindow", "Create Installer"))
        self.removedependentbutton.setText(_translate("MainWindow", "Remove"))
        self.nameinput.setPlaceholderText(_translate("MainWindow", "Project Name"))
        self.label_3.setText(_translate("MainWindow", "Name:"))
        self.addidependentbutton.setText(_translate("MainWindow", "Add"))
        self.label_2.setText(_translate("MainWindow", "Verion:"))
        self.versioninput.setText(_translate("MainWindow", "1.0"))
        self.versioninput.setPlaceholderText(_translate("MainWindow", "Version"))
        self.label.setText(_translate("MainWindow", "Dependent Files/Folders:"))
        self.cleardependentbutton.setText(_translate("MainWindow", "Clear"))
        self.createzipcheck.setText(_translate("MainWindow", "Create a Portable Zip"))
        self.enableconsolecheck.setText(_translate("MainWindow", "Enable Console"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Compiling"))
        self.startupshortcutcheck.setText(_translate("MainWindow", "Startup Shortcut"))
        self.desktopshortcutcheck.setText(_translate("MainWindow", "Desktop Shortcut"))
        self.startmenushortcutcheck.setText(_translate("MainWindow", "Start Menu Shortcut"))
        self.extractionpathinput.setText(_translate("MainWindow", "%appdata%\\{name}"))
        self.label_10.setText(_translate("MainWindow", "Path to Extract:"))
        self.clearfinishedbutton.setText(_translate("MainWindow", "Clear"))
        self.addfinishedbutton.setText(_translate("MainWindow", "Add"))
        self.removefinishedbutton.setText(_translate("MainWindow", "Remove"))
        self.label_11.setText(_translate("MainWindow", "Files to run when finished installing:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Installer"))
        self.label_5.setText(_translate("MainWindow", "Window:"))
        self.iconinput.setPlaceholderText(_translate("MainWindow", "icon.ico"))
        self.windowinput.setPlaceholderText(_translate("MainWindow", "icon.png (Optional)"))
        self.label_4.setText(_translate("MainWindow", "Icon (ico):"))
        self.label_7.setText(_translate("MainWindow", "Text:"))
        self.windowtitleinput.setText(_translate("MainWindow", "{name} v{version} - Installer"))
        self.windowtextinput.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">Thank you for downloading {name}! Please choose your install location.</span></p></body></html>"))
        self.label_8.setText(_translate("MainWindow", "Title:"))
        self.inputfilebrowse_2.setText(_translate("MainWindow", "..."))
        self.inputfilebrowse_3.setText(_translate("MainWindow", "..."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Window/Icon"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("MainWindow", "There is no output yet."))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Verbose"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.setconnections()
    sys.exit(app.exec_())
