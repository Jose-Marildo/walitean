import sys
from PyQt4 import QtGui, QtCore
import walitean
from datetime import datetime

#!/usr/bin/python
#

# Copyright (C) 2014 n0fate
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


####################################################################

class WaliteanUI(QtGui.QWidget):
    def __init__(self):
        super(WaliteanUI, self).__init__()
        self.filename = ''
        self.initUI()   # init

    def initUI(self):
        self.setGeometry(300, 300, 800, 600)
        self.move(300, 300)
        self.setWindowTitle('walitean - WAL Analyzer for SQLite by n0fate')

        # set layout
        mainLayout = QtGui.QVBoxLayout()    # main layout
        topLayout = QtGui.QHBoxLayout()

        QOpenBtn = QtGui.QPushButton('Open WAL File')
        self.connect(QOpenBtn, QtCore.SIGNAL('clicked()'), self.openfile)

        self.Qfilepath = QtGui.QLineEdit()
        QDomainlnk = QtGui.QLabel()
        QDomainlnk.setOpenExternalLinks(1)
        QDomainlnk.setText('<a href="http://forensic.n0fate.com", "_blank">Homepage</a>')

        topLayout.addWidget(QOpenBtn)
        topLayout.addWidget(self.Qfilepath)
        topLayout.addWidget(QDomainlnk)

        self.tablelabel = QtGui.QLabel('Table List')
        self.tablelabel.setFixedWidth(150)
        wallabel = QtGui.QLabel('File Info')
        wallabel.setFixedWidth(150)
        walinfo = QtGui.QTableView()
        walinfo.setFixedWidth(150)
        self.QTableList = QtGui.QListWidget()
        #QTableList.move(50, 100)
        #QTableList.setMinimumSize(50, 250)

        #list_ex = [1,2,3]
        #lv = MyListModel(list_ex)

        #self.QTableList.setModel(lv)

        self.QTableList.setFixedWidth(150)

        self.connect(self.QTableList, QtCore.SIGNAL('itemClicked(QListWidgetItem *)'), self.showRecords)
        self.connect(self.QTableList, QtCore.SIGNAL('itemSelectionChanged()'), self.showRecordskb)


        middleLayout = QtGui.QHBoxLayout()
        leftLayout = QtGui.QVBoxLayout()

        leftLayout.addWidget(self.tablelabel)
        leftLayout.addWidget(self.QTableList)
        leftLayout.addWidget(wallabel)
        leftLayout.addWidget(walinfo)

        rightLayout = QtGui.QVBoxLayout()
        self.recordlabel = QtGui.QLabel('Records')
        self.recordtable = QtGui.QTableWidget()

        #self.connect(self.recordtable, QtCore.SIGNAL('itemClicked(QListWidgetItem *)'), self.recorddump)
        #self.connect(self.recordtable, QtCore.SIGNAL('itemSelectionChanged()'), self.recorddumpkb)
        #self.connect(self.recordtable, QtCore.SIGNAL('currentCellChanged(int,int,int,int)'), self.recorddump)

        rightLayout.addWidget(self.recordlabel)
        rightLayout.addWidget(self.recordtable)

        middleLayout.addLayout(leftLayout)
        middleLayout.addSpacing(3)
        middleLayout.addLayout(rightLayout)

        bottomLayout = QtGui.QHBoxLayout()
        btleftLayout = QtGui.QVBoxLayout()
        btrightLayout = QtGui.QVBoxLayout()


        self.Qcheckheader = QtGui.QCheckBox('Header Analysis')

        self.Qcheckheader.setFixedWidth(140)

        QAnBtn = QtGui.QPushButton('Analysis', self)
        QAnBtn.setFixedWidth(150)
        self.connect(QAnBtn, QtCore.SIGNAL('clicked()'), self.process)
        self.QProgressbar = QtGui.QProgressBar()
        self.QProgressbar.setFixedWidth(140)

        btleftLayout.addWidget(self.Qcheckheader)
        btleftLayout.addWidget(QAnBtn)
        btleftLayout.addWidget(self.QProgressbar)

        self.hexdump = QtGui.QTextBrowser()
        hexdumplabel = QtGui.QLabel('Log')
        self.hexdumpstr = ''
        btrightLayout.addWidget(hexdumplabel)
        btrightLayout.addWidget(self.hexdump)

        bottomLayout.addLayout(btleftLayout)
        middleLayout.addSpacing(3)
        bottomLayout.addLayout(btrightLayout)

        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(middleLayout)
        mainLayout.addLayout(bottomLayout)

        self.setLayout(mainLayout)
        self.show()

    def openfile(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File', QtCore.QDir.homePath())
        self.Qfilepath.setText(self.filename)
        self.writelog('Open File : %s'%self.filename)

    def headeran(self):
        self.writelog('Starting Header Analysis')

        if self.framelist.__len__() == 0:
            self.writelog('No Frame List. Is a valid WAL file?')
            return []

        scheme = []
        for frame in self.framelist:
            if frame[0][0] == 1:    # if page number is 1
                #print 'root page'
                #print '%s'%frame[1][:8]
                #hexdump(frame[1])
                scheme = self.walite.getscheme(frame[1])
                if scheme.__len__() != 0:
                    break

        return scheme

    def tabledetection(self, schemedic):
        self.tablelist = []
        for key, value in self.d.iteritems():
            collist = walitean.DecodeColumn(key)
            print collist
            for tablename, columns in schemedic.iteritems():
                count = 0
                failed = 0
                if (len(columns) - 1) != len(collist):
                    break
                for coltypecnt in range(0, len(columns)):
                    if collist[count] == columns[coltypecnt][1]:
                        count += 1
                        continue
                    elif collist[count] == 'INTEGER' or 'FLOAT' and (columns[coltypecnt][1] == 'INTEGER'):
                        count += 1
                        continue
                    elif collist[count] == 'TEXT' and columns[coltypecnt][1] == 'VARCHAR':
                        count += 1
                        continue
                    elif collist[count] == 'FLOAT' and columns[coltypecnt][1] == 'TIMESTAMP':
                        count += 1
                        continue
                    elif collist[count] == 'UNKNOWN':   # super set
                        count += 1
                        continue
                    else:   # comparing two types
                        failed = 1
                        break
                if failed == 0:
                    print 'find table %s'%tablename
                    break
                else:
                    print('failed to find table')
                    break


    def writelog(self, str):
        self.hexdump.append('%s : %s'%(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str))

    def process(self):

        # Clean-Up
        self.QTableList.clear()
        self.recordtable.clear()
        #self.hexdump.clear()

        if self.filename == '':     # file open error
            self.writelog('Click a Open button and select the WAL File')
            return
        self.walite = walitean.WAL_SQLITE()
        self.walite.open(self.filename)
        self.framelist = self.walite.get_frame_list()

        self.d = self.walite.process(self.framelist)

        self.framecount = self.framelist.__len__()
        self.pagesize = self.walite.pagesize

        if(self.d.__len__() == 0):
            self.writelog('WAL Parsing Failed. Is valid WAL?')
        else:
            #self.showfileinfo()
            if self.Qcheckheader.isChecked():
                self.writelog('Header Analysis enabled')
                scheme = self.headeran()
                if scheme.__len__() == 0:
                    self.writelog('No DB Header Found')
                else:
                    self.tabledetection(scheme)
                self.showtablelist()
            else:
                self.writelog('Header Analysis Disabled')
                self.showtablelist()
            #self.showRecords()


    def showtablelist(self):
        self.QTableList.clear()
        tablenum = self.d.__len__()
        #print tablenum
        self.tablelabel.setText('Table List (%d)'%self.d.__len__())

        for key, value in self.d.iteritems():
            item = QtGui.QListWidgetItem("%s"%key)
            self.QTableList.addItem(item)

    def showRecordskb(self):    # keyboard interrupt handler
        #print self.QTableList.selectedItems()
        self.showRecords(self.QTableList.currentItem())


    def showRecords(self, item):
        self.recordtable.clear()
        encodedcolumn = str(item.text())
        records = self.d[encodedcolumn]

        self.tablename = encodedcolumn # save tablename for hexdump

        # show column list
        columnlist = walitean.DecodeColumn(encodedcolumn)

        #print columnlist

        self.recordtable.setRowCount(len(records))
        #print len(records)
        self.recordtable.setColumnCount(len(columnlist))

        # print Column Name
        self.recordtable.setHorizontalHeaderLabels(QtCore.QStringList(columnlist))

        self.recordlabel.setText('Records (%d)'%records.__len__())

        rownum = 0
        for record in records:
            colnum = 0
            for value in record:
                strelement = ''
                if columnlist[colnum] == 'TEXT':
                    try:
                        #print value
                        strelement = QtGui.QTableWidgetItem(QtCore.QString("%1").arg(value.decode('utf8').replace('\n', ' ')))
                    except UnicodeEncodeError:
                        strelement = QtGui.QTableWidgetItem(QtCore.QString("%1").arg(value.replace('\n', ' ')))
                    except AttributeError:
                        strelement = QtGui.QTableWidgetItem(QtCore.QString("%1").arg(value))
                elif columnlist[colnum] == 'INT':
                    try:
                        strelement = QtGui.QTableWidgetItem(QtCore.QString("%1").arg(int(value)))
                    except TypeError: # None Type
                        strelement = QtGui.QTableWidgetItem(QtCore.QString("%1").arg('Null'))
                else:
                    try:
                        strelement = QtGui.QTableWidgetItem(QtCore.QString("%1").arg(value))
                    except TypeError:
                        strelement = QtGui.QTableWidgetItem(QtCore.QString("Null"))

                strelement.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.recordtable.setItem(rownum, colnum, strelement)
                colnum += 1
            rownum += 1

    # testing pharse
    def recorddump(self, curRow, curCol, preRow, preCol):
        if (curRow == preRow) and (curCol == preCol):
            return

        self.hexdump.clear()

        records = self.d[self.tablename]

        data = records[curRow][curCol]
        output = hexdump(data)
        self.hexdump.setText(output)

    #def showfileinfo(self):
        # showing wal file information

# SOURCE: http://mwultong.blogspot.com/2007/04/python-hex-viewer-file-dumper.html
def hexdump(buf):
    offset = 0
    output = ''
    while offset < len(buf):
        buf16 = buf[offset:offset + 16]
        buf16Len = len(buf16)
        if buf16Len == 0: break
        output += "%08X:  " % (offset)

        for i in range(buf16Len):
            if (i == 8): output += " "
            output += "%02X " % (ord(buf16[i]))

        for i in range(((16 - buf16Len) * 3) + 1):
            output += " "
            if (buf16Len < 9):
                output += " "

        for i in range(buf16Len):
            if (ord(buf16[i]) >= 0x20 and ord(buf16[i]) <= 0x7E):
                output += buf16[i]
            else:
                output += "."

        offset += 16
        output += '\r'
    return output


def main():
    app = QtGui.QApplication(sys.argv)
    wUI = WaliteanUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()