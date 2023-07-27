from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QAction,
    QToolBar,
    QLineEdit,
    QLabel,
    QMenu,
    QCheckBox,
    QSplitter,
) 
from PyQt5.QtCore import Qt, QEvent, QPoint, QSize
from PyQt5.QtGui import QFont, QTextCursor


from pathlib import Path
import sys
import subprocess
import os
import time
import shutil
import qdarktheme
from custom_classes import *



class MainWindow(QMainWindow): 
    def __init__(self,location):
        super().__init__()
        self.location = location
        self.timer = time.time()
        self.selected_items = []
        self.double_click_event = False
        self.clipboard = (None,None)
        self.font = QFont("Terminal",10)
        self.setGeometry(450, 100, 1000, 700)
        self.setWindowTitle(self.location)



        self.forward_stack = []
        self.back_stack = []

        self.toolbars()
        self.favorites_bar()

        self.ui()



    
    def toolbars(self):
        toolbar = QToolBar("Toolbar row 1")
        
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        go_back_button = QAction("Go Back", self)
        go_back_button.setStatusTip("Go Back")
        go_back_button.triggered.connect(self.go_back)
        go_back_button.setFont(self.font)
        toolbar.addAction(go_back_button)

        go_forward_button = QAction("Go Forward", self)
        go_forward_button.setStatusTip("Go Forward")
        go_forward_button.triggered.connect(self.go_forward)
        go_forward_button.setFont(self.font)
        toolbar.addAction(go_forward_button)

        parent_button = QAction("Go To Parent", self)
        parent_button.setStatusTip("Go To Parent")
        parent_button.triggered.connect(self.parent)
        parent_button.setFont(self.font)
        toolbar.addAction(parent_button)

        create_button = QAction("Create", self)
        create_button.setStatusTip("Create a new file")
        create_button.triggered.connect(self.create_window)
        create_button.setFont(self.font)
        self.window2 = None
        toolbar.addAction(create_button)

        self.path_bar = QLineEdit(self.location)
        self.path_bar.returnPressed.connect(self.enter_path)
        self.path_bar.setTextMargins(5,0,5,0)
        self.path_bar.setFont(self.font)
        toolbar.addWidget(self.path_bar)

        toolbar.addWidget(QLabel("       "))

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("search:")
        self.search_bar.setTextMargins(5,0,5,0)
        self.search_bar.setMaximumWidth(300)
        self.search_bar.returnPressed.connect(self.enter_search)
        self.search_bar.setFont(self.font)
        self.is_search = False
        toolbar.addWidget(self.search_bar)


        toolbar.addWidget(QLabel("   "))
        self.addToolBarBreak()
        toolbar2 = QToolBar("Toolbar row 2")
        toolbar2.setMovable(False)
        self.addToolBar(toolbar2)
        
        drop_down = CheckableComboBox()
        drop_down.setFont(self.font)
        drop_down.setMinimumWidth(150)

        drop_down.addItem("File")
        drop_down.setItemChecked(0, True)
        drop_down.addItem("Folder")
        drop_down.setItemChecked(1, True)
        drop_down.addItem("Empty Folder")
        drop_down.setItemChecked(2, True)
        drop_down.addItem("Locked Folder")
        drop_down.setItemChecked(3, True)
        self.filters = [True, True, True, True] # file, folder, empyt folder, locked folder
        drop_down.activated.connect(self.filterer)

        toolbar2.addWidget(QLabel("        "))
        toolbar2.addWidget(drop_down)

        self.sort_box = CheckableComboBox()
        self.sort_box.setFont(self.font)
        self.sort_box.setMinimumWidth(150)
        self.sort_box.addItem("A-Z")
        self.sort_box.setItemChecked(0, True)
        self.sort_box.addItem("Date Modified")
        self.sort_box.setItemChecked(1, False)
        self.sort_box.addItem("Date Created")
        self.sort_box.setItemChecked(2, False)
        self.sort_box.addItem("Size")
        self.sort_box.setItemChecked(3, False)
        self.sort_box.addItem("Acsending")
        self.sort_box.setItemChecked(4, True)
        self.sort_box.activated.connect(self.set_sort)

        toolbar2.addWidget(self.sort_box)

    def favorites_bar(self):
        f = open("favorites.txt","r")
        f = f.read()
        self.favorites_list = f.split("\n")[1:]

        self.favorites = QToolBar("Favorites")
        self.favorites.setMovable(False)
        # self.favorites.setMaximumWidth(200)
        n = QLabel("Favorites")
        n.setAlignment(Qt.AlignCenter)
        n.setFont(self.font)
        self.favorites.addWidget(n)
        for i in range(len(self.favorites_list)):
            btn = self.make_button(self.favorites_list[i])
            btn.setCheckable(False)
            self.favorites.addWidget(btn)
        
        self.favorites.setFixedWidth(200)
        self.addToolBar(Qt.LeftToolBarArea,self.favorites)

    def set_sort(self,x):
        if x < 4 and self.sort_box.itemChecked(x):
            self.sort_box.setItemChecked(0, False)
            self.sort_box.setItemChecked(1, False)
            self.sort_box.setItemChecked(2, False)
            self.sort_box.setItemChecked(3, False)
            self.sort_box.setItemChecked(x, True)
        
        self.ui()

    def apply_sort(self):
        sort_me = []
        if self.sort_box.itemChecked(0):
            self.titles.sort()
        elif self.sort_box.itemChecked(1):
            for i in self.titles:
                create_date = os.path.getctime(self.location + i)
                sort_me.append((i,create_date))
            sort_me.sort(key = lambda x: x[1])
            for i,title in enumerate(sort_me):
                self.titles[i] = title[0]
        elif self.sort_box.itemChecked(2):
            for i in self.titles:
                create_date = os.path.getctime(self.location + i)
                sort_me.append((i,create_date))
            sort_me.sort(key = lambda x: x[1])
            for i,title in enumerate(sort_me):
                self.titles[i] = title[0]
        elif self.sort_box.itemChecked(3):
            for i in self.titles:
                create_date = os.path.getsize(self.location + i)
                sort_me.append((i,create_date))
            sort_me.sort(key = lambda x: x[1])
            for i,title in enumerate(sort_me):
                self.titles[i] = title[0]


        if self.sort_box.itemChecked(4) != True:
            self.titles.reverse()

        # elif self.sort_box.itemChecked(4):
        #     self.titles.sort()

    def filterer(self,x):
        if self.filters[x] == True:
            self.filters[x] = False
        else:
            self.filters[x] = True
        self.ui()

    def create_window(self, checked):
        if self.window2 is None:
            self.window2 = AnotherWindow(self.location)
            self.window2.show()

        else:
            self.window2.close()  # Close window.
            self.window2 = None  # Discard reference.

    def square_ui(self):

        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.lay = QVBoxLayout()
        self.row = QHBoxLayout()
        

        if self.is_search == False:
            self.path_bar.setText(self.location)
            self.titles = os.listdir(self.location)
        else:
            self.is_search = False

        self.apply_sort()
        self.setAcceptDrops(True)

        for i in range(len(self.titles)):
            self.btn = self.make_button(self.titles[i])
            self.btn.setFixedSize(150,100)
            self.btn.setIcon(QIcon())
            text = self.btn.text()
            if len(text) > 15: 
                text = text[:14] + "\n" + text[14:]
                self.btn.setText("\n\n\n\n\n" + text)
            else:
                self.btn.setText("\n\n\n\n\n\n" + text)
            self.btn.setStyleSheet("QPushButton { text-align: center; }")
            # self.btn.setStyleSheet("background-image : url(Tau_Kappa_Epsilon_Coat_of_Arms.png); border-width: 2px;")
            self.btn.setStyleSheet("border-image: url(Tau_Kappa_Epsilon_Coat_of_Arms.png) 0 0 20 0; ")
            if self.filters[self.btn.file_type] == True:
                self.row.addWidget(self.btn)
            if i % 5 == 1:
                self.lay.addLayout(self.row)
                self.row = QHBoxLayout()
        self.lay.addLayout(self.row)

        self.lay.setSpacing(0)
        self.widget.setLayout(self.lay)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.scroll.installEventFilter(self)

        self.setCentralWidget(self.scroll)
            
        
        # self.lay.addStretch(1)


    def ui(self):

        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.lay = QVBoxLayout()

        if self.is_search == False:
            self.path_bar.setText(self.location)
            self.titles = os.listdir(self.location)
        else:
            self.is_search = False

        self.apply_sort()
        self.setAcceptDrops(True)

        for i in range(len(self.titles)):
            self.btn = self.make_button(self.titles[i])
            if self.filters[self.btn.file_type] == True:
                self.lay.addWidget(self.btn)

        self.lay.setSpacing(0)
        self.widget.setLayout(self.lay)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.scroll.installEventFilter(self)

        self.setCentralWidget(self.scroll)
        self.lay.addStretch(1)

    def enter_search(self):
        term = self.search_bar.text().lower()
        self.titles = []
        search_queue = [self.location]
        while len(search_queue) > 0:
            path = search_queue.pop(0)
            try: 
                items = os.listdir(path)
            except:
                continue
            for title in items:
                if term in title.lower():
                    x = path + title
                    self.titles.append(x[len(self.location):])
                if os.path.isdir(path + title + "\\"):
                    search_queue.append(path + title + "\\")
        self.is_search = True
        self.ui()
        
    def eventFilter(self,source, event):

        if event.type() == QEvent.ContextMenu:
            if type(source) == DragDropWidget:
                
                menu = QMenu()
                if source.full_title[0:2] != "C:":
                    rename_button = QAction("Rename")
                    rename_button.triggered.connect(lambda x: self.rename(x,source))
                    menu.addAction(rename_button)

                    delete_button = QAction("Delete")
                    delete_button.triggered.connect(lambda x: self.delete(x,source))
                    menu.addAction(delete_button)

                    copy_button = QAction("Copy")
                    copy_button.triggered.connect(lambda x: self.copy(x,source))
                    menu.addAction(copy_button)

                    cut_button = QAction("Cut")
                    cut_button.triggered.connect(lambda x: self.cut(x,source))
                    menu.addAction(cut_button)
                    if self.clipboard != (None,None):
                        paste_button = QAction("Paste")
                        paste_button.triggered.connect(lambda x: self.paste(x,source))
                        menu.addAction(paste_button)

                    favorite_button = QAction("Add Favorite")
                    favorite_button.triggered.connect(lambda x: self.add_favorite(x,source))
                    menu.addAction(favorite_button)

                remove_favorite_button = QAction("Remove Favorite")
                remove_favorite_button.triggered.connect(lambda x: self.remove_favorite(x,source))
                menu.addAction(remove_favorite_button)

                new_pos = QPoint(event.globalX()+10,event.globalY()+12)
                menu.exec_(new_pos)

                return True
            else:
                menu = QMenu()
                paste_button = QAction("Paste")
                paste_button.triggered.connect(lambda x: self.paste(x,source))
                menu.addAction(paste_button)
                new_pos = QPoint(event.globalX()+10,event.globalY()+12)
                menu.exec_(new_pos)
                return True

        return super().eventFilter(source,event)

    def remove_favorite(self,x,source):
        path1 = self.location + source.text()
        if os.path.exists(path1):
            if path1 in self.favorites_list:
                with open('favorites.txt', 'w') as file2:
                    for i in self.favorites_list:
                        if path1 != i:
                            file2.write("\n" + i)
        self.removeToolBar(self.favorites)
        self.favorites_bar()

    def add_favorite(self,x,source):
        path1 = self.location + source.text()
        if os.path.exists(path1):
            if path1 not in self.favorites_list:
                with open('favorites.txt', 'a') as file2:
                    file2.write("\n" + path1)
        self.removeToolBar(self.favorites)
        self.favorites_bar()

    def paste(self,x,source):
        for path in self.clipboard[0]:
            if self.clipboard[1] == "cut":
                os.rename(path[0],self.location + path[1])
            elif self.clipboard[1] == "copy":
                shutil.copy2(path[0], self.location + path[1])
            btn = self.make_button(path[1])
            i = 0
            for i,name in enumerate(self.titles):
                if name.lower() > btn.new_text().lower():
                    break
            self.lay.insertWidget(i,btn)
            self.titles.insert(i,btn.new_text())

    def cut(self,x,source):
        clipboard_list = []
        for i in range(len(self.titles)):
            test = self.lay.itemAt(i).widget()
            if test.isChecked():
                clipboard_list.append((self.location + test.new_text(),test.new_text()))
        if len(clipboard_list) > 0:
            self.clipboard = (clipboard_list,"cut")
        else:
            self.clipboard = (None,None)

    def copy(self,x,source):
        clipboard_list = []
        for i in range(len(self.titles)):
            test = self.lay.itemAt(i).widget()
            if test.isChecked():
                clipboard_list.append((self.location + test.new_text(),test.new_text()))
        if len(clipboard_list) > 0:
            self.clipboard = (clipboard_list,"copy")
        else:
            self.clipboard = (None,None)

    def delete(self,x,source):
        os.remove(self.location + source.new_text())
        # print("sorry you'll have to edit my code to delete " + source.new_text())
        self.ui()

    def rename(self,x,source):
        rename_text = source.new_text()
        self.rename_box = QLineEdit(source.new_text())
        self.rename_box.selectAll()

        self.rename_box.returnPressed.connect(self.rename_action)
        self.rename_box.setFont(self.font)
        cursor = QTextCursor()
        cursor.setPosition(3)
        index = self.titles.index(rename_text)
        self.renamed_button = self.lay.itemAt(index).widget()
        self.renamed_button.hide()
        self.lay.insertWidget(index,self.rename_box)

    def rename_action(self):

        os.rename(self.location + self.renamed_button.new_text(), self.location + self.rename_box.text())
        # print("thats too much power for one man")

        btn = self.make_button(self.rename_box.text())
        
        for i,name in enumerate(self.titles):
            if name.lower() > btn.new_text().lower():
                break
        self.lay.insertWidget(i,btn)
        self.titles.insert(i,btn.new_text())
        self.rename_box.setParent(None)
        # self.ui()

    def make_button(self,text):
        title = text
        if text[0:2] == "C:":
            title = text.split("\\")[-1]
        btn = DragDropWidget(title)
        
        btn.full_title = text
        icon = QtGui.QIcon()
        if "." in title[1:]:
            btn.file_type = 0
            extention = text.split(".")[-1].lower()
            if extention in ["txt",'log','rtf']: 
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\txt.png"))
            if extention in ["docx",'doc']:
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\word.png"))
            elif extention in ['android','apk']:
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\android.png"))
            elif extention in ['pptx','ppsx','odp']:
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\powerpoint.png"))
            elif extention == "bin":
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\bin.png"))
            elif extention == "py":
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\py.png"))
            elif extention == "zip":
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\zip.png"))
            elif extention == "exe":
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\exe.png"))
            elif extention == "dat":
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\dat.png"))
            elif extention in ['tif','tiff','bmp','jpg','jpeg','png','raw','cr2','nef','orf','sr2','heic']:
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\image.png"))
            elif extention in ['webm','mkv','flv','vod','ogv','ogg','drc','gif','gifv','avi','mts','m2ts','ts','mov','qt','wmv','yuv','rm','rmvb','asf','amv','mp4','m4p',
                               'm4v','mpg','mp2','mpeg','mpe','mpv','mpg','mpeg','m2v','m4v','svi','3gp','3g2','nsv']:
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\video.png"))
            elif extention == "ini":
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\ini.png"))
            elif extention in ["csv",'xlsx','xls','xlsm','dbf','dif','ods',]:
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\spreadsheet.png"))
            elif extention == "sys":
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\sys.png"))
            elif extention == "pdf":
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\pdf.png"))
            else:
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\blank.png"))

        else: # folders
            if "C:" == text[0:2]:
                try: x = os.listdir(text)
                except: x = "locked"
            else:
                try: x = os.listdir(self.location + text)
                except: x = "locked"
            if x == "locked":
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\padlock.png"))
                btn.file_type = 3
            elif x == []:
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\empty folder.png"))
                btn.file_type = 2
            elif "onedrive" in title.lower():
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\onedrive.png"))
                btn.file_type = 1
            elif "downloads" == title.lower():
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\download.png"))
                btn.file_type = 1
            else:
                icon.addPixmap(QtGui.QPixmap("C:\\Users\\leocn\\OneDrive - Drake University\\Documents\\Coding\\file explorer\\icons\\folder.png"))
                btn.file_type = 1


        btn.setIcon(icon)
        btn.setCheckable(True)
        btn.clicked.connect(lambda ch, text=text : self.click_check(text))
        btn.installEventFilter(self)
        btn.setStyleSheet("QPushButton { text-align: left; }")
        btn.setFont(self.font)
        return btn

    def dragEnterEvent(self,event):
        pos = event.pos()
        event.source().setChecked(True)
        event.accept()
    
    def dropEvent(self,event):
        print("oops not yet working")
        pos = event.pos()

        if type(event.source()) == DragDropWidget:
            move_objects = []
            for i in range(len(self.titles)):
                test = self.lay.itemAt(i).widget()
                if test.isChecked():
                    move_objects.append(test.new_text())

            end_point = event.source()

            if os.path.isdir(self.location + end_point.new_text()) and end_point.isChecked() == False:
                for name in move_objects:
                    # os.rename(self.location + name,self.location + end_point.new_text() + "\\" + name)
                    print("Sorry you'll have to edit the fuction to actually move the file")
                self.ui()

    def click_check(self,event):
        
        if .05 < time.time() - self.timer < .5 and self.double_click_event == event:
            if event[0:2] == "C:":
                self.new_location(event, absolute=True)
            else:
                self.new_location(event)
        else:
            self.timer = time.time()
            if event in self.selected_items:
                self.selected_items.remove(event)
            else:
                self.selected_items.append(event)
        self.double_click_event = event

    def parent(self):
        self.search_bar.setText("")
        path = Path(self.location)
        self.back_stack.append(self.location)
        self.location = str(path.parent.absolute()) + "\\"
        self.setWindowTitle(self.location)        
        self.ui()

    def go_forward(self):
        self.search_bar.setText("")
        try:
            self.location = self.forward_stack[-1]
            self.forward_stack.pop()
            self.ui()
        except:
            print("Can't Go Forward")
        self.setWindowTitle(self.location)

    def go_back(self):
        self.search_bar.setText("")
        try:
            self.forward_stack.append(self.location)
            self.location = self.back_stack[-1]
            self.back_stack.pop()
            self.ui()
        except:
            self.forward_stack.pop()
            print("cant go back")
        self.setWindowTitle(self.location)
    
    def new_location(self,path, absolute = False):

        self.search_bar.setText("")
        self.back_stack.append(self.location)
        if absolute == False:
            buffer = self.location + path + "\\"
        else:
            buffer = path + "\\"

        
        if os.path.isdir(buffer):
            try: 
                titles = os.listdir(self.location)
                self.location = buffer
                self.ui()
            except: 
                print("PermissionError")
                self.location = self.back_stack[-1]

        else:
            run = buffer[:-1]
            run = run.replace(" ", "^ ")
            os.startfile(buffer[:-1])

        self.setWindowTitle(self.location)
            
    def enter_path(self):
        if os.path.exists(self.path_bar.text()):
            self.new_location(self.path_bar.text(),True)


class AnotherWindow(QWidget):

    def __init__(self, location):
        super().__init__()
        self.location = location
        self.setWindowTitle("Create File")
        self.font = QFont("Terminal",30)
        self.setFixedSize(500,200)
        layout = QVBoxLayout()

        self.name = QLineEdit()

        self.name.setPlaceholderText("Enter File Name")
        self.name.setFont(self.font)
        self.name.installEventFilter(self)
        layout.addWidget(self.name)

        self.is_dir = QCheckBox("Is this a folder")
        self.is_dir.setFont(self.font)
        layout.addWidget(self.is_dir)

        self.label = QPushButton("create file")
        self.label.setFont(self.font)
        self.label.clicked.connect(self.create_file)
        layout.addWidget(self.label)
        self.setLayout(layout)



    def eventFilter(self,source, event):
        print(event.type())
        # if event.type() == QEvent.InsertParagraphSeparator:
        #     print(True)
        return super().eventFilter(source,event)

    def create_file(self):
        if self.is_dir.isChecked():
            os.makedirs(self.location + self.name.text())
        else:
            f = open(self.location + self.name.text(), "x")

        btn = window.make_button(self.name.text())
        i = 0
        for i,name in enumerate(window.titles):
            if name.lower() > btn.new_text().lower():
                break
        window.lay.insertWidget(i,btn)
        window.titles.insert(i,btn.new_text())
        self.close()



app = QApplication(sys.argv)
qdarktheme.setup_theme()
window = MainWindow("C:\\")
window.show()


sys.exit(app.exec_())


# fixing the drag and drop fuctionality
# reincluding the size and modified date
# zipping and unzipping file
# open with other apps
# keyboard shortcuts
# allow you to change fonts
# moving to parent file
# picture preview