import serial
from time import sleep
from PyQt5.QtWidgets import (QMainWindow, QWidget, QApplication, QHBoxLayout, QMenu, QAction, QMenuBar,
                            QComboBox, QVBoxLayout, QFrame, QLabel, QPushButton, QFileDialog)
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QDateTime
from PyQt5.QtGui import QIcon
import sys
import serial
from serial_port import SerialPort
import pyqtgraph as pg
from statistics import mean
import pandas as pd
import os
import csv

def ressource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except: 
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Arduino(QThread):
    data_received = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.exiting = False
        self.list_data = []
    
    def __del__(self):
        self.exiting = True
        self.wait()
    
    def run(self):
        i = 0
        while not self.exiting:
            self.list_data.append(i)
            i += 1
           
            self.data_received.emit(self.list_data)
           
            if self.exiting:
               break
           
            QThread.msleep(400)
           
        
            
class DataViewer(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cwidget()
        self.create_menu()
        self.generalPartition()
        self.setleftmenuFrame()
        self.setrightmenu()
        self.setPortsetting()
        self.setcurrentDataSection()
        self.setAverageDataSection()
        self.temp_data = []
        self.hum_data = []
        self.Co_data = []
        self.timelist = [0]
        self.space_plotting()
        self.initialtime = (QDateTime.currentDateTime().toString("ss"))
        
    def initUI(self):
        self.setWindowTitle("PureAir Data Viewer")
        self.resize(783, 545)
        self.setStyleSheet("background-color: #1c2125")
        
    def cwidget(self):
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.generalLayout = QHBoxLayout(self.centralWidget)
        
    def create_menu(self):
        menu_Bar = QMenuBar(self)
        menu_Bar.setStyleSheet(
            "background-color: white;"
            "border-radius: 10px;"
        )
        self.setMenuBar(menu_Bar)
        
        file_Menu = QMenu('&File', self)
        file_Menu.setStyleSheet(
            "color: white;"
        )
        save_data = QAction(QIcon(ressource_path("images/file-manager.png")), "Data Acquisition", self)
        save_data.triggered.connect(self.save_data)
        screenshot = QAction(QIcon(ressource_path("images/screen.png")), "Screenshots", self)
        screenshot.triggered.connect(self.screenshoot_)
        file_Menu.addAction(save_data)
        file_Menu.addAction(screenshot)
        
        exit_menu = QMenu('&Exit', self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        exit_menu.addAction(exit_action)
        
        tools_Menu = QMenu('&Tools', self)
        tools_Menu.setStyleSheet(
            'color: white;'
        )
        refresh_action = QAction(QIcon(ressource_path('images/refresh.png')), "&Refresh Port", self)
        refresh_action.triggered.connect(self.refresh_port)
        refresh_action.setShortcut("Ctrl+R")
        tools_Menu.addAction(refresh_action)
        preference_submenu = QMenu("&Preferences")
        tools_Menu.addMenu(preference_submenu)
        
        clear_graph_action = QAction(QIcon(ressource_path("images/graph-clear.png")), "&Clear Graph", self)
        tools_Menu.addAction(clear_graph_action)
        clear_graph_action.triggered.connect(self.clear_graph)
        
        menu_Bar.addMenu(file_Menu)
        menu_Bar.addMenu(tools_Menu)
        menu_Bar.addMenu(exit_menu)
        
        menu_Bar.setNativeMenuBar(False)
        
    
    def refresh_port(self):
        self.list_port.clear()
        self.list_port.addItems(self.display_list_port())
        
    def screenshoot_(self):
        screen = QApplication.primaryScreen()
        pixmap_ = screen.grabWindow(0)
        img, _ = QFileDialog.getSaveFileName(self,"PureAir",
                                            filter="PNG(*.png);; JPEG(*.jpg)")
        if img[-3:] == "png":
            pixmap_.save(img, "png")
        elif img[-3:] == "jpg":
            pixmap_.save(img, "jpg")
    
    
    
    def save_data(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)", options=options)

        if filename:
            # Write to the CSV file
            with open(filename, mode='w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['Time', 'Temperature', 'Humidity', 'CO'])
                for i in range(len(self.temp_data)):
                    writer.writerow([self.timelist[i], self.temp_data[i], self.hum_data[i], self.Co_data[i]])
        
        
    def generalPartition(self):
        self.leftmenu = QFrame(self.centralWidget)
        self.leftmenu.setMaximumSize(QSize(270, 16777215))
        self.leftmenu.setMinimumSize(QSize(270, 16777215))
        self.leftmenu.setFrameShape(QFrame.StyledPanel)
        self.leftmenu.setFrameShadow(QFrame.Raised)
        self.vleftlayout = QVBoxLayout(self.leftmenu)
        self.leftmenu.setStyleSheet(
            "border-radius: 10px;"
        )
        self.generalLayout.addWidget(self.leftmenu)
        
        self.rightmenu = QFrame(self.centralWidget)
        self.vrightmenulayout = QVBoxLayout(self.rightmenu)
        self.generalLayout.addWidget(self.rightmenu)
        
    def setleftmenuFrame(self):
        self.currentdataframe = QFrame(self.leftmenu)
        self.currentdataframe.setFrameShape(QFrame.StyledPanel)
        self.currentdataframe.setFrameShadow(QFrame.Raised)
        self.currentdataframe.setStyleSheet(
            "background-color:#32373a;"
            "border-radius: 10px;"
        )
        self.currentdatalayout = QHBoxLayout(self.currentdataframe)
        self.vleftlayout.addWidget(self.currentdataframe)
        
        self.averageframe = QFrame(self.leftmenu)
        self.averageframe.setFrameShadow(QFrame.Raised)
        self.averageframe.setFrameShape(QFrame.StyledPanel)
        self.averageframe.setStyleSheet(
            "background-color: #32373A;"
            "border-radius: 10px;"
        )
        self.h_averagelayout = QHBoxLayout(self.averageframe)
        self.vleftlayout.addWidget(self.averageframe)
        
        
    def setrightmenu(self):
        self.portframe = QFrame(self.rightmenu)
        self.portframe.setMaximumSize(QSize(16777215, 70))
        self.hportlayout = QHBoxLayout(self.portframe)
        self.vrightmenulayout.addWidget(self.portframe)
        
        self.plottingframe = QFrame(self.rightmenu)
        self.playout = QVBoxLayout(self.plottingframe)
        self.vrightmenulayout.addWidget(self.plottingframe)
        
    def setPortsetting(self):
        self.list_port = QComboBox(self.portframe)
        self.list_port.setMinimumHeight(30)
        self.list_port.setStyleSheet(
            "color: #F2F3F4;"
            "background-color: gray;"
            "border-radius: 10px;"
        )
        self.list_port.addItems(self.display_list_port())
        self.hportlayout.addWidget(self.list_port)
        
        self.open_port_button = QPushButton(self.portframe)
        self.open_port_button.setShortcut('Ctrl+O+P')
        self.open_port_button.setText("Open Port")
        self.open_port_button.setMinimumHeight(30)
        self.open_port_button.clicked.connect(self.open_port_clicked)
        self.open_port_button.clicked.connect(self.sendthread)
        self.open_port_button.setStyleSheet(
            "QPushButton"
            "{"
            "background-color: gray;"
            "border-radius: 10px;"
            "}"
            "QPushButton::pressed"
            "{"
            "background-color:green;"
            "}"
        )
        self.hportlayout.addWidget(self.open_port_button)
        
        self.close_port_button = QPushButton(self.portframe)
        self.close_port_button.setText("Close Port")
        self.close_port_button.setShortcut('Ctrl+C+P')
        self.close_port_button.setMinimumHeight(30)
        self.close_port_button.clicked.connect(self.close_port_clicked)
        self.close_port_button.setStyleSheet(
            "QPushButton"
            "{"
            "background-color: gray;"
            "border-radius: 10px;"
            "}"
            "QPushButton::pressed"
            "{"
            "background-color:green;"
            "}"
        )
        self.hportlayout.addWidget(self.close_port_button)
        
    def display_list_port(self):
        self.sp = SerialPort()
        list_port = self.sp.get_portlist()
        return list_port
        
    def open_port_clicked(self):
        try:
            port_name = self.list_port.currentText()
            ser = serial.Serial(port_name, 9600)
            self.sp.ser = ser
            print(self.sp.port_isOpen())
            self.sp.open_port()
        except:
            pass
        
    def close_port_clicked(self):
        try:
            self.thread.exiting = True
            self.sp.close_port()
            print(self.sp.port_isOpen())
        except:
            pass
        
    def space_plotting(self):
        self.graph = pg.PlotWidget(self.plottingframe)
        self.graph.setBackground("#1c2125")
        self.graph.setLabel("bottom", "time")
        self.graph.setLabel("left", "Datas")
        self.graph.showGrid(True, True)
        self.graph.setAutoPan(x=True)
        self.playout.addWidget(self.graph)
        self.legendItem = pg.LegendItem((80,60), offset=(70,20))
        self.legendItem.setParentItem(self.graph.graphicsItem())
        p1 = self.graph.plot(self.hum_data, pen=pg.mkPen(255, 0, 0))
        p2 = self.graph.plot(self.temp_data, pen=pg.mkPen(102, 224, 255))
        p3 = self.graph.plot(self.Co_data, pen=pg.mkPen(0, 255, 0))
        self.legendItem.addItem(p1, "Humidity")
        self.legendItem.addItem(p2, "Temperature")
        self.legendItem.addItem(p3, "Carbon Monoxyde")
    
    def setcurrentDataSection(self):
        self.variablesframe = QFrame(self.currentdataframe)
        self.variablesframe.setFrameShadow(QFrame.Raised)
        self.variablesframe.setFrameShape(QFrame.StyledPanel)
        """self.variablesframe.setStyleSheet(
            "background-color: red;"
        )"""
        self.variablesframelayout = QVBoxLayout(self.variablesframe)
        
        dateLbel = QLabel(self.variablesframe)
        dateLbel.setStyleSheet('color: white')
        dateLbel.setText("Hour")
        dateLbel.setAlignment(Qt.AlignLeft)
        
        temperatureLbel = QLabel(self.variablesframe)
        temperatureLbel.setStyleSheet('color: white')
        temperatureLbel.setText("Temperature")
        temperatureLbel.setAlignment(Qt.AlignLeft)
        
        humiditylabel = QLabel(self.variablesframe)
        humiditylabel.setStyleSheet('color: white')
        humiditylabel.setText("Humidity")
        humiditylabel.setAlignment(Qt.AlignLeft)
        
        monoxydelabel = QLabel(self.variablesframe)
        monoxydelabel.setStyleSheet('color: white')
        monoxydelabel.setText("smoke")
        monoxydelabel.setAlignment(Qt.AlignLeft)
        
        self.variablesframelayout.addWidget(dateLbel)
        self.variablesframelayout.addWidget(temperatureLbel)
        self.variablesframelayout.addWidget(humiditylabel)
        self.variablesframelayout.addWidget(monoxydelabel)
        
        self.currentdatalayout.addWidget(self.variablesframe)
        
        self.data1frame = QFrame(self.currentdataframe)
        self.data1frame.setFrameShape(QFrame.StyledPanel)
        self.data1frame.setFrameShadow(QFrame.Raised)
        self.data1layout = QVBoxLayout(self.data1frame)
        self.currentdatalayout.addWidget(self.data1frame)
        
        date = QDateTime.currentDateTime()
        self.datedata = QLabel(self.data1frame)
        self.datedata.setText(date.toString("HH:mm:ss"))
        self.datedata.setStyleSheet('color: white')
        self.datedata.setAlignment(Qt.AlignRight)
        
        self.tempdata = QLabel(self.data1frame)
        self.tempdata.setStyleSheet('color: white')
        self.tempdata.setText('0')
        self.tempdata.setAlignment(Qt.AlignRight)
        
        self.humiditydata = QLabel(self.data1frame)
        self.humiditydata.setStyleSheet('color: white')
        self.humiditydata.setText('0')
        self.humiditydata.setAlignment(Qt.AlignRight)
        
        self.monoxydedata = QLabel(self.data1frame)
        self.monoxydedata.setStyleSheet('color: white')
        self.monoxydedata.setText('0')
        self.monoxydedata.setAlignment(Qt.AlignRight)
        
        self.data1layout.addWidget(self.datedata)
        self.data1layout.addWidget(self.tempdata)
        self.data1layout.addWidget(self.humiditydata)
        self.data1layout.addWidget(self.monoxydedata)
        
    def setAverageDataSection(self):
        self.variable2frame = QFrame(self.averageframe)
        self.variable2frame.setFrameShadow(QFrame.Raised)
        self.variable2frame.setFrameShape(QFrame.StyledPanel)
        self.v2framelayout = QVBoxLayout(self.variable2frame)
        
        time2 = QLabel(self.variable2frame)
        time2.setStyleSheet('color: white')
        time2.setText("Time")
        time2.setAlignment(Qt.AlignLeft)
        
        temperature = QLabel(self.variable2frame)
        temperature.setStyleSheet('color: white')
        temperature.setAlignment(Qt.AlignLeft)
        temperature.setText("Temperature")
        
        humidity = QLabel(self.variable2frame)
        humidity.setStyleSheet('color: white')
        humidity.setText("Humidity")
        humidity.setAlignment(Qt.AlignLeft)
        
        CO_val = QLabel(self.variable2frame)
        CO_val.setAlignment(Qt.AlignLeft)
        CO_val.setStyleSheet('color: white')
        CO_val.setText("CO")
        
        self.v2framelayout.addWidget(time2)
        self.v2framelayout.addWidget(temperature)
        self.v2framelayout.addWidget(humidity)
        self.v2framelayout.addWidget(CO_val)
        
        self.h_averagelayout.addWidget(self.variable2frame)
        self.data2frame = QFrame(self.averageframe)
        self.data2layout = QVBoxLayout(self.data2frame)
        self.h_averagelayout.addWidget(self.data2frame)
        
        self.timedata = QLabel(self.data2frame)
        self.timedata.setStyleSheet('color: white')
        self.timedata.setText("0s")
        self.timedata.setAlignment(Qt.AlignRight)
        
        self.temp_average = QLabel(self.data2frame)
        self.temp_average.setStyleSheet('color: white')
        self.temp_average.setAlignment(Qt.AlignRight)
        self.temp_average.setText("0C")
        
        self.hum_average = QLabel(self.data2frame)
        self.hum_average.setStyleSheet('color: white')
        self.hum_average.setText("0%")
        self.hum_average.setAlignment(Qt.AlignRight)
        
        self.monoxyde_average = QLabel(self.data2frame)
        self.monoxyde_average.setStyleSheet('color: white')
        self.monoxyde_average.setText("0%")
        self.monoxyde_average.setAlignment(Qt.AlignRight)
        
        self.data2layout.addWidget(self.timedata)
        self.data2layout.addWidget(self.temp_average)
        self.data2layout.addWidget(self.hum_average)
        self.data2layout.addWidget(self.monoxyde_average)
        
        
    def mean_value(self, values):
        return mean(values)
        
    def sendthread(self):
        self.thread = Arduino()
        self.thread.data_received.connect(self.signal_Accepted)
        self.thread.start()
        
        
    def signal_Accepted(self):
        
        try:
            values = self.sp.get_data()
            i, j , k = values[0], values[1], values[2]
            self.temp_data.append(i)
            self.hum_data.append(j)
            self.Co_data.append(k)
            
            self.tempdata.setText(str(i) + "C")
            self.humiditydata.setText(str(j) + "%")
            self.monoxydedata.setText(str(k) + "%")
            self.datedata.setText(QDateTime.currentDateTime().toString("HH:mm:ss"))
            
            self.timedata.setText(QDateTime.currentDateTime().toString("yyyy/MM/dd"))
            self.temp_average.setText(str(round(self.mean_value(self.temp_data), 3)))
            self.hum_average.setText(str(round(self.mean_value(self.hum_data), 4)))
            self.monoxyde_average.setText(str(round(self.mean_value(self.Co_data), 4)))
            
            t = self.timelist[-1] + 0.4
            self.timelist.append(t)
            p1 = self.graph.plot(self.hum_data, pen=pg.mkPen(255, 0, 0))
            p2 = self.graph.plot(self.temp_data, pen=pg.mkPen(102, 224, 255))
            p3 = self.graph.plot(self.Co_data, pen=pg.mkPen(0, 255, 0))
            

        except: 
            self.thread.exiting = True
            
    def clear_graph(self):
        self.graph.clear()
        

        
def main():
    app = QApplication(sys.argv)
    win = DataViewer()
    win.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()    
