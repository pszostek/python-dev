#!/usr/bin/env python

from __future__ import division
from PySide import QtCore, QtGui
from PySide.QtCore import QStandardItemModel, QStandardItem
import time
from tree_model import *


class TreeViewDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor("grey"))
        painter.setPen(pen)
        painter.drawRect(option.rect)


class MyTableModel(QtGui.QStandardItemModel):
    def data(self, index, role):
        if not index.isValid():
            return QtGui.QStandardItemModel.data(self, index, role)
        if role == QtCore.Qt.BackgroundRole:
            value = self.data(index, QtCore.Qt.DisplayRole)
            if value is None:
                return QtGui.QColor("white")
            r, g, b = 0, 0, 0
            if 1/8 <= value and value <= 1/8:
                r = 0
                g = 0
                b = 4*value + .5
            elif 1/8 < value and value <= 3/8:
                r = 0
                g = 4*value - .5
                b = 0
            elif 3/8 < value and value <= 5/8:
                r = 4*value - 1.5
                g = 1
                b = -4*value + 2.5
            elif (5/8 < value and value <= 7/8):
                r = 1
                g = -4*value + 3.5
                b = 0
            elif (7/8 < value and value <= 1):
                r = -4*value + 4.5
                g = 0
                b = 0
            else:
                r = .5
                g = 0
                b = 0
            return QtGui.QColor.fromRgb(255*r, 255*g, 255*b, 100)
        return QtGui.QStandardItemModel.data(self, index, role)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, nr_columns, rows):
        super(MainWindow, self).__init__()

        self.setupModel(nr_columns, rows)
        self.setupViews()
        self.statusBar()
        self.resize(870, 550)

    def setupModel(self, nr_columns, rows):
        self.model = QStandardItemModel()
        root = self.model.invisibleRootItem()
        i1, i2, i3 = QStandardItem(1), QStandardItem(2), QStandardItem(3)
        root.appendRow([i1, i2, i3]) 
        self.model.insertRow(0)
        self.model.setData(QModelIndex(), [1,2,3])
        self.model.setData(QModelIndex(), [5,6,7])
        self._set_data(nr_columns, rows)

    def _set_data(self, nr_columns, rows):
        start_time = time.time()
        # for row_idx, row in enumerate(rows):
        #     if row_idx % 10 != 0:
        #         pass
        #     self.model.insertRows(row_idx, 1, QtCore.QModelIndex())
        #     for col_idx, col in enumerate(row):
        #         self.model.setData(self.model.index(row_idx, col_idx, QtCore.QModelIndex()),
        #                            col)
        end_time = time.time()
        self.statusBar().showMessage("Inserted data in %g" % (end_time - start_time))

    def setupViews(self):
        splitter = QtGui.QSplitter()
        self.table = QtGui.QTreeView()
        self.table.setItemDelegate(TreeViewDelegate())
        self.table.setModel(self.model)
        splitter.addWidget(self.table)

     #   button = QtGui.QPushButton('Shuffle', self)
     #   button.clicked.connect(self.shuffle)
     #   button.resize(button.sizeHint())
     #   splitter.addWidget(button)

        self.selectionModel = QtGui.QItemSelectionModel(self.model)
        self.table.setSelectionModel(self.selectionModel)
        self.setCentralWidget(splitter)

    def shuffle(self):
        from random import random as rnd
        row_count = self.model.rowCount()
        column_count = self.model.columnCount()
        new_rows = [[str(rnd())[:4] for _ in xrange(column_count)] for _ in xrange(row_count)]
        start_time = time.time()
        self.model.clear()
        for row_idx, row in enumerate(new_rows):
            self.model.insertRow(row_idx, row)
        end_time = time.time()
        self.statusBar().showMessage("Reset data in %g" % (end_time - start_time))


if __name__ == '__main__':

    import sys
    import csv
    with open('sample.csv', 'rb') as csvfile:
        sample_reader = csv.reader(csvfile, delimiter=',')
        rows = list(sample_reader)
        rows = [map(float, row) for row in rows]
    rows = rows[:500]
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(30, rows)
    window.show()
    window.showMaximized()
    sys.exit(app.exec_())
