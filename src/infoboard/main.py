import os
import sys
import mimetypes
import inspect
import yaml
from pathlib import Path

from typing import Union

from dataclasses import dataclass, field
from datetime import datetime
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

import vlc

SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
ROOT_FOLDER = os.path.realpath(os.path.join(SCRIPT_FOLDER, '..', '..'))
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
SLIDE_TIME = 60

@dataclass
class Media:
    url: str

    def correct(self) -> bool:
        return os.path.isfile(self.url)

    @classmethod
    def from_dict(cls, env):
        return cls(**{
            k: v for k, v in env.items()
            if k in inspect.signature(cls).parameters
        })

@dataclass
class Image(Media):
    slide_time: int = None

@dataclass
class Video(Media):
    pass

@dataclass
class Configuration:
    default_slide_time: int = SLIDE_TIME
    default_media_dir: str = DATA_DIR
    media: list[Union[Media, dict]] = field(default_factory=list)
    auto_update: bool = False

    def __post_init__(self):
        new_media = []
        for element in self.media:
            if isinstance(element, dict):
                url = element.get('url')
                element_media = Media(url)
                if not element_media.correct():
                    element_media = Media(os.path.join(self.default_media_dir, url))
                    element.update({'url': element_media.url})
                if element_media.correct():
                    element_media.url = os.path.realpath(element_media.url)
                    mime = mimetypes.guess_type(element_media.url)[0]
                    if mime is not None:
                        if mime.startswith('image'):
                            img = Image.from_dict(element)
                            if img.slide_time is None:
                                img.slide_time = self.default_slide_time
                            new_media.append(img)
                        elif mime.startswith('video'):
                            new_media.append(Video.from_dict(element))
        self.media = new_media

    @classmethod
    def from_dict(cls, env):
        return cls(**{
            k: v for k, v in env.items()
            if k in inspect.signature(cls).parameters
        })

@dataclass
class AppData:
    configuration_file: str = None
    config_last_update: float = datetime.timestamp(datetime.now())
    config: Configuration = None
    media_index: int = 0
    mes: list = field(default_factory=list)

    def __post_init__(self):
        self.mes.append(str(self.configuration_file))
        if self.configuration_file is None:
            self.configuration_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',
                                                   'data', 'config.yaml')
        with open(self.configuration_file, 'r') as cfg:
            config_dict = yaml.safe_load(cfg)
            self.config = Configuration.from_dict(config_dict)
        self.update()

    def update(self):
        # if os.path.getmtime(self.configuration_file) > self.config_last_update:
        with open(self.configuration_file, 'r') as cfg:
            config_dict = yaml.safe_load(cfg)
            self.config = Configuration.from_dict(config_dict)
        self.config_last_update = datetime.timestamp(datetime.now())

        # if self.config.auto_update == True:
        #     try:
        #         from os import listdir
        #         from os.path import isfile, join
        #         onlyfiles = [os.path.realpath(os.path.join(self.config.default_media_dir, f)) for f in os.listdir(self.config.default_media_dir) if os.path.isfile(os.path.join(self.config.default_media_dir, f))]
        #         self.mes.append(str(onlyfiles))
        #         cfg_urls = [media.url for media in self.config.media]
        #         self.mes.append(str(cfg_urls))
        #         new_files = [f for f in onlyfiles if f not in cfg_urls]
        #         self.mes.append(str(new_files))
        #         files_update = []
        #         for new_file in new_files:
        #             mime = mimetypes.guess_type(new_file)[0]
        #             if mime is not None:
        #                 if mime.startswith('image') or mime.startswith('video'):
        #                     files_update.append({'url': new_file})
        #         self.mes.append(str(files_update))
        #         if files_update:
        #             with open(self.configuration_file, 'r') as cfg:
        #                 config_dict = yaml.safe_load(cfg)
        #             config_dict['media'] += files_update
        #             with open(self.configuration_file, 'w') as cfg:
        #                 yaml.dump(config_dict, cfg)
        #     except Exception as e:
        #         self.mes.append(str(e))

    def get_next(self) -> Union[Media, None]:
        if not self.config.media:
            return None
        if self.media_index >= len(self.config.media):
            self.media_index = 0
        next_media = self.config.media[self.media_index]
        if isinstance(next_media, dict) or not next_media.correct():
            self.config.media.pop(self.media_index)
            return self.get_next()
        else:
            self.media_index += 1
            return next_media

class MainWindow(QMainWindow):
    def __init__(self, app_data: AppData, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.setStyleSheet("background-color: white;")
        self.setWindowTitle("InfoBoard-Pi")
        self.geometry_info = QRect(0, 0, 1920, 1080)
        self.current_image = None
        self.current_video = None
        self.images = []
        self.videos = []
        self.setCursor(Qt.BlankCursor)
        self.setGeometry(self.geometry_info)
        self.process = None
        self.setCentralWidget(LogoStart())
        self.vlc_instance = vlc.Instance()
        self.mediaplayer = self.vlc_instance.media_player_new()
        # QTimer.singleShot(5000, self.run_info)

    def run_info(self):
        pass
        #Path(f'{ROOT_FOLDER}/.alive').touch()
        #QTimer.singleShot(1000, self.run_info)

    def next_media(self):
        self.setStyleSheet("background-color: black;")
        self.app_data.update()
        media = self.app_data.get_next()
        if media is None:
            self.no_media()
        else:
            if isinstance(media, Image):
                self.show_image(media)
            else:
                self.show_video_embedded(media)

    def show_image(self, media):
        self.setGeometry(self.geometry_info)
        # self.current_image = media.url
        image_widget = ImageViewer(image=media.url, size=self.size())
        self.setCentralWidget(image_widget)

        QTimer.singleShot(media.slide_time * 1000, self.next_media)

    def show_video(self, media):
        if media is not None:
            self.process = QProcess()
            self.process.finished.connect(self.video_change_state)
            self.process.start(f"vlc --fullscreen --no-mouse-events --no-osd --no-audio --intf dummy {media.url} vlc://quit")

            video_widget = VideoPlayer()
            self.setCentralWidget(video_widget)

        else:
            self.video_change_state()

    def show_video_embedded(self, media):
        if media is not None:
            vlc_player = VideoPlayer(media, self.mediaplayer)
            self.setCentralWidget(vlc_player)
            QTimer.singleShot(200, lambda: self.start_video_embedded(vlc_player))
            vlc_player.play()
        else:
            self.next_media()

    def start_video_embedded(self, vlc_player):
        vlc_player.play()
        QTimer.singleShot(1000, lambda: self.check_video(vlc_player))

    def check_video(self, vlc_player):
        print(vlc_player.is_stopped())
        if not vlc_player.is_stopped():
            QTimer.singleShot(200, lambda: self.check_video(vlc_player))
        else:
            self.next_media()


        # video_widget = VideoPlayer()
        # self.setCentralWidget(video_widget)
        # self.video_to_play = media
        # QTimer.singleShot(200, self.start_video)
        #    # video_widget.play(self.current_video, self.video_change_state, self.show_image)
        # process = QProcess()
        # # print(f'play video {self.current_video}')
        # process.start(f"vlc --fullscreen --no-osd --intf dummy {media.url} vlc://quit")
        # process.waitForFinished(-1)
        # process.close()
        # self.video_change_state(0)

    # def start_video(self):
    #     if self.video_to_play is not None:
    #         self.process = QProcess()
    #         self.process.finished.connect(self.video_change_state)
    #         self.process.start(f"vlc --fullscreen --no-osd --intf dummy {self.video_to_play.url} vlc://quit")
    #         self.video_to_play = None
    #
    #     else:
    #         self.video_change_state()

    def start_show(self):
        QTimer.singleShot(2000, self.next_media)

    def video_change_state(self):
        if isinstance(self.process, QProcess):
            self.process.close()
        self.process = None
        self.next_media()

    def no_media(self,):
        self.setGeometry(self.geometry_info)
        # self.current_image = media.url
        self.setStyleSheet("background-color: white;")
        widget = NoMedia(self.app_data)
        self.setCentralWidget(widget)
        QTimer.singleShot(10 * 1000, self.next_media)

class NoMedia(QWidget):
    def __init__(self, appdata: AppData, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white;'")
        self.setLayout(QVBoxLayout())
        self.layout().addStretch()
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()
        logo_layout.addWidget(Logo())
        logo_layout.addStretch()
        self.layout().addLayout(logo_layout)
        self.layout().addStretch()
        text_layout = QHBoxLayout()
        text_layout.addStretch()
        label = QLabel('NO MEDIA')
        label.setStyleSheet('QLabel{color: #bf6262; font-size: 16pt}')
        text_layout.addWidget(label)
        text_layout.addStretch()
        self.layout().addLayout(text_layout)
        self.layout().addStretch()


class ImageViewer(QLabel):
    def __init__(self, image: str, size: QSize, parent=None):
        super().__init__(parent)
        self.image = QPixmap(image).scaled(size, aspectRatioMode=Qt.KeepAspectRatioByExpanding,
                                           transformMode=Qt.SmoothTransformation)
        self.setPixmap(self.image)

class Logo(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QPixmap(os.path.join(os.path.dirname(__file__),'logo.png'))
        self.setPixmap(self.image)

class LogoStart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white;")
        self.setLayout(QVBoxLayout())
        self.layout().addStretch()
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()
        logo_layout.addWidget(Logo())
        logo_layout.addStretch()
        self.layout().addLayout(logo_layout)
        self.layout().addStretch()
        text_layout = QHBoxLayout()
        text_layout.addStretch()
        text_layout.addWidget(QLabel('Version 0.1'))
        text_layout.addStretch()
        self.layout().addLayout(text_layout)
        self.layout().addStretch()

class VideoPlayer(QWidget):
    def __init__(self, media, mediaplayer, parent=None):
        super().__init__(parent)
        self.mediaplayer = mediaplayer
        self.media = media
        self.palette = self.palette()
        self.palette.setColor (QPalette.Window,
                               QColor(0,0,0))
        self.setPalette(self.palette)
        self.setAutoFillBackground(True)
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()
        self.vlc_media = self.instance.media_new(media.url)
        # put the media in the media player
        self.mediaplayer.set_media(self.vlc_media)
        self.frame = QFrame(self)
        self.widget_layout = QHBoxLayout()
        self.widget_layout.addWidget(self.frame)
        self.setLayout(self.widget_layout)


    def play(self):
        self.mediaplayer.set_xwindow(int(self.frame.winId()))
        self.mediaplayer.play()

    def is_stopped(self):
        return not self.mediaplayer.is_playing()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    geometry = app.desktop().availableGeometry()
    window = MainWindow(AppData())
    window.setGeometry(geometry)
    window.showFullScreen()
    # window.show()
    window.start_show()
    sys.exit(app.exec_())
