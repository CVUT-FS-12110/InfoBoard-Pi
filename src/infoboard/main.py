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
        self.setWindowTitle("InfoBoard-Pi")
        self.geometry_info = QRect(0, 0, 1920, 1080)
        self.current_image = None
        self.current_video = None
        self.images = []
        self.videos = []
        self.setCursor(Qt.BlankCursor)
        self.setGeometry(self.geometry_info)
        QTimer.singleShot(1000, self.run_info)

    def run_info(self):
        Path(f'{ROOT_FOLDER}/.alive').touch()
        QTimer.singleShot(1000, self.run_info)

    def next_media(self):
        self.app_data.update()
        media = self.app_data.get_next()
        if media is None:
            self.no_media()
        else:
            if isinstance(media, Image):
                self.show_image(media)
            else:
                self.show_video(media)

    def show_image(self, media):
        self.setGeometry(self.geometry_info)
        # self.current_image = media.url
        image_widget = ImageViewer(image=media.url, size=self.size())
        self.setCentralWidget(image_widget)

        QTimer.singleShot(media.slide_time * 1000, self.next_media)

    def show_video(self, media):
        video_widget = VideoPlayer()
        self.setCentralWidget(video_widget)
           # video_widget.play(self.current_video, self.video_change_state, self.show_image)
        process = QProcess()
        # print(f'play video {self.current_video}')
        process.start(f"vlc --fullscreen --intf dummy {media.url} vlc://quit")
        process.waitForFinished(-1)
        process.close()
        self.video_change_state(0)

    def start_show(self):
        QTimer.singleShot(2000, self.next_media)

    def video_change_state(self, state):
        if state == 0:
            self.next_media()

    def no_media(self,):
        self.setGeometry(self.geometry_info)
        # self.current_image = media.url
        widget = NoMedia(self.app_data)
        self.setCentralWidget(widget)
        QTimer.singleShot(60 * 1000, self.next_media)

class NoMedia(QWidget):
    def __init__(self, appdata: AppData, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel('No media, adding log:'))
        for log in appdata.mes:
            self.layout().addWidget(QLabel(log))

class ImageViewer(QLabel):
    def __init__(self, image: str, size: QSize, parent=None):
        super().__init__(parent)
        self.image = QPixmap(image).scaled(size, aspectRatioMode=Qt.KeepAspectRatioByExpanding,
                                           transformMode=Qt.SmoothTransformation)
        self.setPixmap(self.image)


class VideoPlayer(QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    geometry = app.desktop().availableGeometry()
    window = MainWindow(AppData())
    window.setGeometry(geometry)
    window.showFullScreen()
    # window.show()
    window.start_show()
    sys.exit(app.exec_())
