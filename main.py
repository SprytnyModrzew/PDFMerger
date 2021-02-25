import sys
import re
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QPushButton, QDialog, QListWidget, \
    QListWidgetItem, QVBoxLayout, QCheckBox, QLabel, QLineEdit, QFrame, QGridLayout, QSizePolicy, QWidget, QTableWidget, \
    QTableWidgetItem
from PySide6.QtGui import QIntValidator, QValidator
# from PyQt5 import QtWidgets
from qt_material import apply_stylesheet
import pdfmodifier

cachedPDF = []


# https://pypi.org/project/qt-material/
# https://gist.github.com/peace098beat/db8ef7161508e6500ebe
# https://stackoverflow.com/questions/5671354/how-to-programmatically-make-a-horizontal-line-in-qt
# https://realpython.com/pdf-python/

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class PopupWidget(QWidget):
    def __init__(self, message):
        super().__init__()
        print(message.creator)
        self.table = QTableWidget(7, 2)

        self.label = QLabel("poop")
        # todo bugged mess
        self.setLayout(self.layout)
        self.layout.addWidget(self.label)


class MainWidget(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Merger")
        self.resize(720, 360)
        self.setAcceptDrops(True)
        self.mainLayout = QHBoxLayout()

        self.listLayout = QVBoxLayout()
        self.listOptionsLayout = QHBoxLayout()
        self.list = QListWidget()

        self.listLayout.addWidget(self.list)
        self.listLayout.addLayout(self.listOptionsLayout)

        self.listOptions = {
            "up": QPushButton("Move up"),
            "down": QPushButton("Move down"),
            "remove": QPushButton("Remove")
        }
        self.listOptionsLayout.addWidget(self.listOptions["up"])
        self.listOptionsLayout.addWidget(self.listOptions["down"])
        self.listOptionsLayout.addWidget(self.listOptions["remove"])

        self.listOptions["up"].clicked.connect(self.list_item_move_up)
        self.listOptions["down"].clicked.connect(self.list_item_move_down)
        self.listOptions["remove"].clicked.connect(self.list_item_remove)

        self.options = QVBoxLayout()

        self.pagesLayout = QHBoxLayout()
        self.pageDefinitions = {
            "label": QLabel("Pages included:"),
            "max": QLineEdit(),
            "min": QLineEdit(),
            "interlude": QLabel("/")
        }
        self.pageDefinitions["max"].setDisabled(True)
        self.pageDefinitions["min"].setDisabled(True)
        self.pagesLayout.addWidget(self.pageDefinitions["label"])
        self.pagesLayout.addWidget(self.pageDefinitions["min"])
        self.pagesLayout.addWidget(self.pageDefinitions["interlude"])
        self.pagesLayout.addWidget(self.pageDefinitions["max"])

        self.optionDefinitions = {
            "info": QPushButton("About"),
            "merge": QPushButton("Merge"),
            "passwordCheck": QCheckBox("Password protected?"),
            "unlockHint": QLabel("Password:"),
            "unlock": QPushButton("Unlock"),
            "unlockEdit": QLineEdit(""),
            "lockCheck": QCheckBox("Output encrypted?"),
            "lockEdit": QLineEdit(""),
            "lockHint": QLabel("Password:")
        }

        self.options.addWidget(self.optionDefinitions["info"])
        self.options.addWidget(self.optionDefinitions["merge"])
        self.options.addWidget(QHLine())
        self.options.addLayout(self.pagesLayout)
        self.options.addWidget(QHLine())
        self.options.addWidget(self.optionDefinitions["passwordCheck"])
        self.options.addWidget(self.optionDefinitions["unlockHint"])
        self.options.addWidget(self.optionDefinitions["unlockEdit"])
        self.options.addWidget(self.optionDefinitions["unlock"])

        self.options.addWidget(QHLine())
        self.options.addWidget(self.optionDefinitions["lockCheck"])

        self.options.addWidget(self.optionDefinitions["lockHint"])
        self.options.addWidget(self.optionDefinitions["lockEdit"])

        self.optionDefinitions["passwordCheck"].stateChanged.connect(self.showUnlockWindow)
        self.optionDefinitions["lockCheck"].stateChanged.connect(self.showLockWindow)
        self.optionDefinitions["merge"].clicked.connect(self.merge_pdf)
        self.optionDefinitions["info"].clicked.connect(self.showInfo)
        self.optionDefinitions["unlock"].clicked.connect(self.decrypt_pdf)

        self.list.itemSelectionChanged.connect(self.selection_change)
        self.pageDefinitions["min"].editingFinished.connect(self.page_min_change)
        self.pageDefinitions["max"].editingFinished.connect(self.page_max_change)

        self.mainLayout.addLayout(self.listLayout)

        self.mainLayout.addWidget(QVLine())

        self.mainLayout.addLayout(self.options)

        self.setLayout(self.mainLayout)
        self.showUnlockWindow()
        self.showLockWindow()

    def page_min_change(self):
        try:
            x = self.pageDefinitions["min"].validator().validate(self.pageDefinitions["min"].text(), 0)
            y = pdfmodifier.get_max_pages(cachedPDF[self.list.currentRow()]["path"])
            print(x)
            print(cachedPDF)
            if x[0] != 2:
                if int(x[1]) > y:
                    self.pageDefinitions["min"].setText(str(y))
                    cachedPDF[self.list.currentRow()]["min"] = y
                else:
                    self.pageDefinitions["min"].setText(str(1))
                    cachedPDF[self.list.currentRow()]["min"] = 1
            else:
                cachedPDF[self.list.currentRow()]["min"] = int(self.pageDefinitions["min"].text())
            self.list.currentItem().setText(self.format_list_item_name(self.list.currentRow()))
        except AttributeError:
            pass
        return

    def page_max_change(self):
        try:
            x = self.pageDefinitions["max"].validator().validate(self.pageDefinitions["max"].text(), 0)
            y = pdfmodifier.get_max_pages(cachedPDF[self.list.currentRow()]["path"])
            print(cachedPDF)
            if x[0] != 2:
                if int(x[1]) > y:
                    self.pageDefinitions["max"].setText(str(y))
                    cachedPDF[self.list.currentRow()]["max"] = y
                else:
                    self.pageDefinitions["max"].setText(str(1))
                    cachedPDF[self.list.currentRow()]["max"] = 1
            else:
                cachedPDF[self.list.currentRow()]["max"] = int(self.pageDefinitions["max"].text())
            if int(x[1]) < int(cachedPDF[self.list.currentRow()]["min"]):
                print("happend")
                self.pageDefinitions["max"].setText(str(min([cachedPDF[self.list.currentRow()]["min"], y])))
                cachedPDF[self.list.currentRow()]["max"] = min([cachedPDF[self.list.currentRow()]["min"], y])
            self.list.currentItem().setText(self.format_list_item_name(self.list.currentRow()))
        except AttributeError:
            pass
        return

    def format_list_item_name(self, index):
        return cachedPDF[index]["path"].split('/')[-1].split('.')[0] + " pages:" + str(
            cachedPDF[index]["min"]) + "-" + str(cachedPDF[index]["max"])

    def selection_change(self):
        if len(cachedPDF) == 0:
            self.pageDefinitions["max"].setDisabled(True)
            self.pageDefinitions["min"].setDisabled(True)
            return
        x = pdfmodifier.get_max_pages(cachedPDF[self.list.currentRow()]["path"])
        print(x)
        self.pageDefinitions["min"].setText(str(cachedPDF[self.list.currentRow()]["min"]))
        self.pageDefinitions["max"].setText(str(cachedPDF[self.list.currentRow()]["max"]))
        self.pageDefinitions["min"].setValidator(QIntValidator(1, x))
        self.pageDefinitions["max"].setValidator(QIntValidator(1, x))
        self.pageDefinitions["max"].setDisabled(False)
        self.pageDefinitions["min"].setDisabled(False)

    def list_item_move_up(self):
        print(len(cachedPDF))
        if len(cachedPDF) > 1 and self.list.currentRow() != 0:
            cachedPDF[self.list.currentRow()], cachedPDF[self.list.currentRow() - 1] = cachedPDF[
                                                                                           self.list.currentRow() - 1], \
                                                                                       cachedPDF[self.list.currentRow()]
            x = self.list.currentRow() - 1
            print(cachedPDF)
            y = len(cachedPDF)
            for _ in range(0, y):
                self.list.takeItem(0)
            for i in cachedPDF:
                self.list.addItem(i["item"])
            self.list.setCurrentRow(x)

    def list_item_move_down(self):
        print(len(cachedPDF))
        if len(cachedPDF) > 1 and self.list.currentRow() != len(cachedPDF) - 1:
            cachedPDF[self.list.currentRow()], cachedPDF[self.list.currentRow() + 1] = cachedPDF[
                                                                                           self.list.currentRow() + 1], \
                                                                                       cachedPDF[self.list.currentRow()]
            x = self.list.currentRow() + 1
            print(cachedPDF)
            y = len(cachedPDF)
            for _ in range(0, y):
                self.list.takeItem(0)
            for i in cachedPDF:
                self.list.addItem(i["item"])
            self.list.setCurrentRow(x)

    def list_item_remove(self):
        x = self.list.currentRow()
        self.list.takeItem(x)
        cachedPDF.pop(x)
        print(cachedPDF)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def merge_pdf(self):
        paths = [{"path": i["path"], "min": i["min"], "max": i["max"]} for i in cachedPDF]
        print(paths)
        pdfmodifier.merge_pdfs(paths=paths, output='output.pdf')
        if self.optionDefinitions["lockCheck"].isChecked():
            pdfmodifier.add_encryption('output.pdf', 'output.pdf', self.optionDefinitions["lockEdit"].text())

    def decrypt_pdf(self):
        pdfmodifier.unlock(cachedPDF[self.list.currentRow()]["path"], self.optionDefinitions["unlockEdit"].text())

    def showUnlockWindow(self):
        x = not self.optionDefinitions["passwordCheck"].isChecked()
        self.optionDefinitions["unlockHint"].setDisabled(x)
        self.optionDefinitions["unlock"].setDisabled(x)
        self.optionDefinitions["unlockEdit"].setDisabled(x)
        return

    def showLockWindow(self):
        x = not self.optionDefinitions["lockCheck"].isChecked()
        self.optionDefinitions["lockHint"].setDisabled(x)
        self.optionDefinitions["lockEdit"].setDisabled(x)
        return

    def showInfo(self):
        print(cachedPDF[self.list.currentRow()]["path"])
        info = pdfmodifier.extract_information(cachedPDF[self.list.currentRow()]["path"])
        self.window = PopupWidget(info)
        self.window.show()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            if re.search(".?[.]pdf", f):
                print("woop")
                # self.list.addItem(QListWidgetItem(f))
                print(f.split('/')[-1])
                x = pdfmodifier.get_max_pages(f)
                cachedPDF.append({
                    "path": f,
                    "item": QListWidgetItem(f.split('/')[-1].split('.')[0] + " pages:1-" + str(x)),
                    "min": 1,
                    "max": x
                })

                self.list.addItem(cachedPDF[-1]["item"])
                self.list.setCurrentRow(len(cachedPDF) - 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_amber.xml')
    ui = MainWidget()
    ui.show()
    sys.exit(app.exec_())
# setup stylesheet
