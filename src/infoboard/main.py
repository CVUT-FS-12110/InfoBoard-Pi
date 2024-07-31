import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import struct

from PyQt5 import QtSvg
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis


IMAGES_DIR = '/media/zat/usb/images'
VIDEOS_DIR = '/media/zat/usb/videos'
SLIDE_TIME = 1000 * 60 
DASH_TIME = 1000 * 60 

class MainWindow(QMainWindow):
    def __init__(self, geometry, parent=None):
        super().__init__(parent)
        self.setWindowTitle("U12137 / DICE Vitrina App")
        self.geometry_info = QRect(0, 0, 1920, 1080)
        self.current_image = None
        self.current_video = None
        self.images = []
        self.videos = []
        self.setCursor(Qt.BlankCursor)
        self.setGeometry(self.geometry_info)
        with requests.Session() as s:
                self.dataprovider = DataProvider(s)

    def update_images(self):
        try:
                self.images = [os.path.join(IMAGES_DIR, f) for f in os.listdir(IMAGES_DIR)
                               if os.path.isfile(os.path.join(IMAGES_DIR, f))]
        except:
                self.images = []

    def show_image(self):
        self.setGeometry(self.geometry_info)
        self.update_images()
        if len(self.images) > 0:
            try:
                index = self.images.index(self.current_image) + 1
            except ValueError:
                index = 0

            if index >= len(self.images):
                index = 0

            self.current_image = self.images[index]
            image_widget = ImageViewer(image=self.images[index], size=self.size())
            self.setCentralWidget(image_widget)
        else:
            self.show_dash()

        QTimer.singleShot(SLIDE_TIME, self.show_dash)

    def show_dash(self):
        # to solve problem width non-standard pictures in image view
        dummy_widget = QWidget()
        dummy_widget.setFixedSize(self.geometry_info.width(), self.geometry_info.height())
        self.setCentralWidget(dummy_widget)
        self.setGeometry(self.geometry_info)      
        dash = Dash(self.dataprovider)
        dash.setFixedSize(self.geometry_info.width(), self.geometry_info.height())
        self.setCentralWidget(dash)
        dash.resize(self.geometry_info.x(), self.geometry_info.y())
        QTimer.singleShot(DASH_TIME, self.show_video)


    def update_videos(self):
        try:
                self.videos = [os.path.abspath(os.path.join(VIDEOS_DIR, f)) for f in os.listdir(VIDEOS_DIR)
                               if os.path.isfile(os.path.join(VIDEOS_DIR, f))]
        except:
                self.videos = []

    def show_video(self):
        self.update_videos()
        if len(self.videos) > 0:
            try:
                index = self.videos.index(self.current_video) + 1
            except ValueError:
                index = 0

            if index >= len(self.videos):
                index = 0

            self.current_video = self.videos[index]
            video_widget = VideoPlayer()
            if isinstance(self.centralWidget(), Dash):
                self.centralWidget().timer_data.stop()
                self.centralWidget().chart1.timer_anim.stop()
                self.centralWidget().chart1.timer_data.stop()
                self.centralWidget().chart2.timer_anim.stop()
                self.centralWidget().chart2.timer_data.stop()
                self.centralWidget().chart3.timer_anim.stop()
                self.centralWidget().chart3.timer_data.stop()
            self.setCentralWidget(video_widget)
#            video_widget.play(self.current_video, self.video_change_state, self.show_image)
            process = QProcess()
            # print(f'play video {self.current_video}')
            process.start(f"/usr/bin/vlc --fullscreen --no-osd {self.current_video} vlc://quit")
            process.waitForFinished(-1)
            print('\n\n')
            print(process.readAllStandardOutput())
            print(process.readAllStandardError())
            process.close()
            self.video_change_state(0)

        else:
                self.video_change_state(0)

    def start_show(self):
        QTimer.singleShot(200, self.show_dash)

    def video_change_state(self, state):
        if state == 0:
            self.show_dash()

class ImageViewer(QLabel):
    def __init__(self, image: str, size: QSize, parent=None):
        super().__init__(parent)
        self.image = QPixmap(image).scaled(size, aspectRatioMode=Qt.KeepAspectRatioByExpanding,
                                           transformMode=Qt.SmoothTransformation)
        self.setPixmap(self.image)

class VideoPlayer(QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_widget = QMediaPlayer()

    def play(self, uri: str, change_slot, error_slot):
        self.media_widget.setMedia(QMediaContent(QUrl.fromLocalFile(uri)))
        self.media_widget.setVideoOutput(self)
        self.media_widget.stateChanged.connect(change_slot)
        self.media_widget.error.connect(error_slot)
        self.media_widget.play()

@dataclass
class Data:
    max_length: int = 100
    index: list[datetime] = field(default_factory=list)
    otacky: list = field(default_factory=list)
    vykon: list = field(default_factory=list)
    zasah: list = field(default_factory=list)
    zadane_otacky: list = field(default_factory=list)
    zadany_vykon: list = field(default_factory=list)
    zatezujici_moment: list = field(default_factory=list)

    def append(self, otacky, vykon, zasah, zadane_otacky, zadany_vykon, zatezujici_moment):
        self.index.append(datetime.now())
        self.otacky.append(otacky*50)
        self.vykon.append(vykon*100)
        self.zasah.append(zasah*100)
        self.zadane_otacky.append(zadane_otacky/2)
        self.zadany_vykon.append(zadany_vykon)
        self.zatezujici_moment.append(zatezujici_moment)

        if len(self.index) > self.max_length:
            self.index.pop(0)
            self.otacky.pop(0)
            self.vykon.pop(0)
            self.zasah.pop(0)
            self.zadane_otacky.pop(0)
            self.zadany_vykon.pop(0)
            self.zatezujici_moment.pop(0)

class DataProvider:
    def __init__(self, session):
        self.session = session
        self.url = "http://192.168.11.1/data.php"
        self.data_req =   'DATA=S*R*10*R*11*R*12*B*1*B*2*B*3*B*4*B*5*B*6*B*7*B*8*B*9*B*13*B*14*B*15*B*16*B*17*B*18*B*19*B*20*R*21*R*22*R*23*R*24*B*25*B*26*B*27*B*28'

        self.headers =  {"Accept":"application/json, text/plain, */*",
                         "Origin": 'http://192.168.11.1',
                         'Referer': 'http://192.168.11.1/svg.html/edit',
                         'Host': '192.168.11.1',
                         'Content-Type': 'application/x-www-form-urlencoded'}



        g=session.get(self.url)
        p = session.post(self.url, data='DATA=S*I*0', cookies=self.session.cookies, headers=self.headers)
        self.timer = QTimer()
        self.timer.timeout.connect(self.get_data)
        self.data = Data()
        self.rucne = False
        self.fazovano = False
        self.zapnuto = True
        

        
        self.get_data()

    def get_data(self):
        p = self.session.post(self.url, data=self.data_req, cookies=self.session.cookies, headers=self.headers)
        
        data_list=p.text.split('*')
        data = {'B': {}, 'R': {}, 'I': {}}
        for idx in range(1, len(data_list), 3):
             if data_list[idx] == 'B':
                data[data_list[idx]][int(data_list[idx+1])] = bool(int(data_list[idx+2]))
             elif data_list[idx] == 'R':
                 data[data_list[idx]][int(data_list[idx+1])] = struct.unpack('!f',bytes.fromhex(data_list[idx+2]))[0]
                                 
        #print(data['B'])
        #print(data['R'])

        self.data.append(data['R'][11],
                         data['R'][10],
                         data['R'][12],
                         data['R'][22],
                         data['R'][24],
                         data['R'][23],
                         )
        self.rucne = data['B'][25]
        self.fazovano = data['B'][27]
        self.zapnuto = data['B'][26]
        self.timer.start(1000)
        
        #self.data.append(np.random.uniform(),
        #                 np.random.uniform(),
        #                 np.random.uniform(),
        #                 )
        #self.rucne = bool(np.round(np.random.uniform()))
        #self.fazovano = bool(np.round(np.random.uniform()))
        #self.zapnuto = bool(np.round(np.random.uniform()))
        #self.timer.start(1000+int(np.random.uniform(0.05, 0.5)*1000))

class Dash(QWidget):
    def __init__(self, dataprovider: DataProvider, parent=None):
        super().__init__(parent)
        self.dataprovider = dataprovider
        self.dash_layout = QVBoxLayout()
        self.dash_widget = QWidget()
        self.dash_widget.setObjectName('dashboard')
        
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        #self.title = QLabel('Live PLC stream')
        #self.title.setFont(QFont('Arial', 40))
        #self.main_layout.addWidget(self.title)

#        self.title1 = QLabel('Otáčky')
        #self.title1.setFont(QFont('Arial', 20))
        #self.main_layout.addWidget(self.title1, 1, 1)

        self.data_widget1 = QWidget()
        self.data_widget1.setLayout(QHBoxLayout())
        self.chart1 = DataChart(dataprovider, 0)
        self.data_widget1.layout().addWidget(self.chart1)
        self.main_layout.addWidget(self.data_widget1, 1, 1)

        #self.title2 = QLabel('Výkon')
        #self.title2.setFont(QFont('Arial', 20))
        #self.main_layout.addWidget(self.title2, 3, 1)

        self.data_widget2 = QWidget()
        self.data_widget2.setLayout(QHBoxLayout())
        self.chart2 = DataChart(dataprovider, 1)
        self.data_widget2.layout().addWidget(self.chart2)
        self.main_layout.addWidget(self.data_widget2, 2, 1)
        
        #self.title3 = QLabel('Akční zásah')
        #self.title3.setFont(QFont('Arial', 20))
        #self.main_layout.addWidget(self.title3, 5, 1)        
                
        self.data_widget3 = QWidget()
        self.data_widget3.setLayout(QHBoxLayout())
        self.chart3 = DataChart(dataprovider, 2)
        self.data_widget3.layout().addWidget(self.chart3)
        self.main_layout.addWidget(self.data_widget3, 3, 1)
        
        self.main_layout.addItem(QSpacerItem(10, 10), 0, 0)
        self.main_layout.addItem(QSpacerItem(1920-1110, 20), 4, 2)
        
        #self.data_text_widget = QWidget()
        #self.data_text_widget.setFixedWidth(600)1080-610
        #self.data_text_widget.setLayout(QVBoxLayout())
        #self.zapnuto_label = QLabel()
        #self.zapnuto_label.setFont(QFont('Arial', 40))
        #self.data_text_widget.layout().addWidget(self.zapnuto_label)
        #self.fazovano_label = QLabel()
        #self.fazovano_label.setFont(QFont('Arial', 40))
        #self.data_text_widget.layout().addWidget(self.fazovano_label)
        #self.manual_label = QLabel()
        #self.manual_label.setFont(QFont('Arial', 40))
        #self.data_text_widget.layout().addWidget(self.manual_label)
        #self.data_widget.layout().addWidget(self.data_text_widget)
        #self.timer_data = QTimer()
        #self.timer_data.timeout.connect(self.update_data_text)
        #self.update_data_text()

        #self.describe = QWidget()
        #self.describe.setFixedHeight(400)
        #self.describe.setLayout(QHBoxLayout())
        #self.describe_label = QLabel()
        #self.describe_label.setFont(QFont('Arial', 20))
        #self.describe_label.setText("""
        #Bla bla bla ..
        #bla..
        #bla bla bla bla..
        #bla..
        #""")
        #self.describe.layout().addWidget(self.describe_label)

        #self.logo_widget = QWidget()
        #self.logo_widget.setLayout(QVBoxLayout())
        #self.logo_widget.layout().addStretch()
        #self.logo = SvgWidget('zat.svg')
        # self.logo.setMaximumWidth(600)
        #self.logo_widget.setMinimumHeight(300)
        #self.logo_widget.layout().addWidget(self.logo)
        #self.logo_widget.setMaximumWidth(600)
        #self.describe.layout().addStretch()
        #self.describe.layout().addWidget(self.logo_widget)

        #self.main_layout.addWidget(self.describe)
        
        self.setObjectName('dashboard')
        self.setStyleSheet("#dashboard {background-image: url(/home/zat/Scripts/zatpi/data/schema_zat_fazovano.png); background-position: top-left;}")
        self.dash_layout.addWidget(self.dash_widget)
        self.dash_layout.setSpacing(0)
        self.dash_layout.setContentsMargins(0, 0, 0, 0)
        self.dash_widget.setLayout(self.main_layout)
        self.setLayout(self.dash_layout)
        self.timer_data = QTimer()
        self.timer_data.timeout.connect(self.update_data)
        self.update_data()


    def update_data(self):
        if self.dataprovider.fazovano:
            self.setStyleSheet("#dashboard {background-image: url(/home/zat/Scripts/zatpi/data/schema_zat_fazovano.png); background-position: top-left;}")
        else:
            self.setStyleSheet("#dashboard {background-image: url(/home/zat/Scripts/zatpi/data/schema_zat_ostrov.png); background-position: top-left;}") 

        #self.zapnuto_label.setText(f'Zapnuto: {self.dataprovider.zapnuto}')
        #self.fazovano_label.setText(f'Fazovano: {self.dataprovider.fazovano}')
        #self.manual_label.setText(f'Ručně: {self.dataprovider.rucne}')
        self.timer_data.start(200)
        #print(self.objectName())
        #print(self.styleSheet())

class DataChart(QChartView):
    def __init__(self, dataprovider: DataProvider, kind: int, parent=None):
        super().__init__(parent)
        self.dataprovider = dataprovider
        self.data = dataprovider.data

        self.setChart(QChart())
        self.chart().layout().setContentsMargins(0, 0, 0, 0);
        self.chart().setBackgroundRoundness(0);
        self.chart().setMargins(QMargins(0, 0, 0, 0))

        self.x_axis = QDateTimeAxis()
        self.x_axis.setFormat("h:mm:ss");
        self.y_axis = QValueAxis()
        
        self.kind = kind
        
        if self.kind == 0:
                self.y_axis_max = np.max(self.data.otacky) + 5
        elif self.kind == 1:
                self.y_axis_max = np.max(self.data.vykon) + 5
        else:
                self.y_axis_max = np.max(self.data.zasah) + 5

        self.chart().addAxis(self.x_axis, Qt.AlignBottom)
        self.chart().addAxis(self.y_axis, Qt.AlignLeft)



        if self.kind == 0:
                self.otacky = QLineSeries(name='Otáčky turbíny/generátoru [Hz]')
                self.zadane_otacky = QLineSeries(name='Požadované otáčky [Hz]')
                self.chart().addSeries(self.otacky)
                self.chart().addSeries(self.zadane_otacky)

                self.otacky.attachAxis(self.x_axis)
                self.otacky.attachAxis(self.y_axis)

                pen = self.otacky.pen()
                pen.setColor(QColor('red'))
                self.otacky.setPen(pen)
              
                self.zadane_otacky.attachAxis(self.x_axis)
                self.zadane_otacky.attachAxis(self.y_axis)
                
                pen = self.zadane_otacky.pen()
                pen.setStyle(Qt.DotLine)
                pen.setColor(QColor('pink'))
                self.zadane_otacky.setPen(pen)
        elif self.kind == 1:
                self.vykon = QLineSeries(name='Výkon generátoru [%]')
                self.zadany_vykon = QLineSeries(name='Požadovaný výkon [%]')
                self.chart().addSeries(self.vykon)
                self.chart().addSeries(self.zadany_vykon)
                self.vykon.attachAxis(self.x_axis)
                self.vykon.attachAxis(self.y_axis)

                pen = self.vykon.pen()
                pen.setColor(QColor('blue'))
                self.vykon.setPen(pen)
                
                self.zadany_vykon.attachAxis(self.x_axis)
                self.zadany_vykon.attachAxis(self.y_axis)

                pen = self.zadany_vykon.pen()
                pen.setStyle(Qt.DotLine)
                pen.setColor(QColor('violet'))
                self.zadany_vykon.setPen(pen)
        else:
                self.zasah = QLineSeries(name='Akční zásah - otevření rozvodného kola [%]')
                self.chart().addSeries(self.zasah)
                self.zasah.attachAxis(self.x_axis)
                self.zasah.attachAxis(self.y_axis)

                pen = self.zasah.pen()
                pen.setColor(QColor('green'))
                self.zasah.setPen(pen)

#        self.zatezujici_moment = QLineSeries(name='Zatezujici moment')
#        self.chart().addSeries(self.zatezujici_moment)
        
        #self.SP = QLineSeries()

        # self.zatezujici_moment.attachAxis(self.x_axis)
        # self.zatezujici_moment.attachAxis(self.y_axis)
        
        # pen = self.zatezujici_moment.pen()
        # pen.setStyle(Qt.DotLine)
        # pen.setColor(QColor('orange'))
        # self.zatezujici_moment.setPen(pen)


        self.timer_data = QTimer()
        self.timer_anim = QTimer()
        self.timer_data.timeout.connect(self.append_data)
        self.timer_anim.timeout.connect(self.move_chart)

        self.append_data()
        self.move_chart()

    def append_data(self):
        otacky = []
        vykon = []
        zasah = []
        zadane_otacky = []
        zadany_vykon = []
        zatezujici_moment = []
        
        if self.kind == 0:
                for idx, index in enumerate(self.data.index):
                    dateidx = int(index.timestamp() * 1000)
                    otacky.append(QPointF(dateidx, self.data.otacky[idx]))
                    zadane_otacky.append(QPointF(dateidx, self.data.zadane_otacky[idx]))

                self.otacky.replace(otacky)
                self.zadane_otacky.replace(zadane_otacky)
                if self.dataprovider.fazovano:
                        self.zadane_otacky.setVisible(False)
                else:
                        self.zadane_otacky.setVisible(True)

        elif self.kind == 1:
                for idx, index in enumerate(self.data.index):
                    dateidx = int(index.timestamp() * 1000)
                    vykon.append(QPointF(dateidx, self.data.vykon[idx]))
                    zadany_vykon.append(QPointF(dateidx, self.data.zadany_vykon[idx]))

                self.vykon.replace(vykon)
                self.zadany_vykon.replace(zadany_vykon)
                if self.dataprovider.fazovano:
                        self.zadany_vykon.setVisible(True)
                else:
                        self.zadany_vykon.setVisible(False)

        else:
                for idx, index in enumerate(self.data.index):
                    dateidx = int(index.timestamp() * 1000)
                    zasah.append(QPointF(dateidx, self.data.zasah[idx]))
#                    zatezujici_moment.append(QPointF(dateidx, self.data.zatezujici_moment[idx]))

                self.zasah.replace(zasah)
#        self.zatezujici_moment.replace(zatezujici_moment)

        self.timer_data.start(1000)

    def move_chart(self):
        now = datetime.now()
        self.x_axis.setRange(now-timedelta(seconds=98), now-timedelta(seconds=2))
        if self.kind == 0:
                maxy = np.max([np.max(self.data.otacky), np.max(self.data.zadane_otacky)]) + 5
        elif self.kind == 1:
                maxy = np.max([np.max(self.data.vykon), np.max(self.data.zadany_vykon)]) + 5
        else:
                maxy = np.max([np.max(self.data.zasah)]) + 5
        if self.y_axis_max < maxy:
            self.y_axis_max += np.min([maxy - self.y_axis_max, 0.5 if self.kind > 0 else 0.25])
        elif self.y_axis_max > maxy:
            self.y_axis_max -= np.min([self.y_axis_max - maxy, 0.5 if self.kind > 0 else 0.25])
        self.y_axis.setRange(0, self.y_axis_max)
        self.update()
        self.timer_anim.start(100)


class SvgWidget(QtSvg.QSvgWidget):

    def __init__(self, *args):
        super().__init__(*args)

    def paintEvent(self, event):
        renderer = self.renderer()
        if renderer is not None:
            painter = QPainter(self)
            size = renderer.defaultSize()
            ratio = size.height()/size.width()
            length = min(self.width(), self.height())
            renderer.render(painter, QRectF(0, 0, length, ratio * length))
            painter.end()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    geometry = app.desktop().availableGeometry()
    window = MainWindow(geometry)
    #window.show()
    print(geometry)
    window.setGeometry(geometry)
    window.showFullScreen()
    window.start_show()
    sys.exit(app.exec_())
