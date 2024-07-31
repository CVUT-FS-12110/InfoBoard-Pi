import os
import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget


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
            self.show_image()

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
