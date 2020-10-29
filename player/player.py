# -*- coding: utf-8 -*-
import sys, vlc, socket, os.path, threading, json, re, requests
from _thread import *
# from time import sleep
from player_api import api
from time_format import timeFormat
from pymongo import MongoClient
from PyQt5.QtWidgets import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *

db_client = MongoClient("mongodb://localhost:27017/MediaServer")
db = db_client['MediaServer']

instance = vlc.Instance()
player = instance.media_player_new()

port = 12302
MEDIA_PATH = os.path.join(os.path.expanduser("~"),'media')

class PlayerServer(QVideoWidget):
    songFinishedEvent = pyqtSignal()
    def __init__(self):
        super().__init__()        
        self.setupUI()
        self.playlist = None
        self.mediafile = None
        self.curr_time = None
        self.duration = None
        self.fullscreenCurrent = False
        self.udpServer = udpServer()
        self.udpServer.start()
        self.udpServer.play.connect(self.play)
        self.udpServer.stop.connect(self.stop)
        self.udpServer.pause.connect(self.pause)
        self.udpServer.fullscreen.connect(self.fullscreen)
        self.udpServer.udpSender.connect(self.udpSender)
        self.songFinishedEvent.connect(self.udpServer.songFinished)
        self.setNewPlayer()       
        self.show()

        self.setup = db.setup.find_one({})
        print (self.setup)
        try:
            if self.setup['fullscreen'] == True:
                self.fullscreen()
                self.fullscreenCurrent = True
            else:
                self.fullscreenCurrent = False

            if self.setup['poweronplay'] == True:
                file = db.playlist.find_one({'playid': 0}, { 'complete_name': 1 })['complete_name']
                # sleep(5)
                self.play(file)
        except:
            pass

    def setupUI(self):
        self.setWindowTitle("MEDIA SERVER")
        self.setWindowIcon(QIcon('favicon_player.ico'))
        self.setStyleSheet("background-color: black;")
        # self.logo = QLabel(self)
        # # self.logo.setText("1234")
        # self.logo.resize(1920,1080)
        # self.pix = QPixmap()
        # self.pix.load("logo.png")
        # # self.pix = self.pix.scaledToWidth(600)
        # self.logo.setPixmap(self.pix)
        # self.logo.setAlignment(Qt.AlignCenter)

    def setNewPlayer(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.winId())
        self.setEventManager()

    def setEventManager(self):
        self.Event_Manager = self.player.event_manager()
        self.Event_Manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.songFinished) #meida end
        self.Event_Manager.event_attach(vlc.EventType.MediaPlayerLengthChanged, self.getMediaLength, self.player) #media length
        self.Event_Manager.event_attach(vlc.EventType.MediaPlayerTimeChanged, self.getCurrentTime, self.player) #emdia get currnet time

    @pyqtSlot(str)
    def udpSender(self, msg):
        self.udpSendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSendSock.sendto(msg.encode(), (self.setup['rtIp'], self.setup['rtPort']))
        self.udpSendSock.close()
    
    def setMedia(self, mediaFile):
        self.media = self.instance.media_new(mediaFile)
        self.player.set_media(self.media)

    @pyqtSlot(str)
    def play(self, mediaFile):
        if self.mediafile == mediaFile: self.player.stop()
        else: self.mediafile = mediaFile; self.setMedia(mediaFile)
        self.player.play()
        self.fullscreen()

    @pyqtSlot()
    def pause(self):
        self.player.pause()

    @pyqtSlot()
    def stop(self):
        self.player.stop()
        self.mediafile = None

    @pyqtSlot()
    def fullscreen(self):
        self.setup = db.setup.find_one({})
        if self.fullscreenCurrent != self.setup['fullscreen']:
            self.setFullScreen(self.setup['fullscreen'])
            self.fullscreenCurrent = self.setup['fullscreen']

    def songFinished(self,evnet):
        self.songFinishedEvent.emit()

    def getMediaLength(self, time, player):
        sendTime = timeFormat(time.u.new_length)
        if self.duration != sendTime:
            self.duration = sendTime
            start_new_thread(self.udpSender, ('length,{}'.format(sendTime),))

    def getCurrentTime(self, time, player):
        if self.setup['progress']:
            start_new_thread(self.currentTimeProcess, (time,))
    
    def currentTimeProcess(self, time):
        sendTime = timeFormat(time.u.new_time)
        if self.curr_time != sendTime:
            self.curr_time = sendTime
            self.udpSender('current,{}'.format(sendTime))


class udpServer(QThread):
    play = pyqtSignal(str)
    stop = pyqtSignal()
    pause = pyqtSignal()
    fullscreen = pyqtSignal()
    udpSender = pyqtSignal(str)

    def __init__(self, parent = None):
        super(udpServer, self).__init__(parent)        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        print("Udp Server Start {} : {}".format('0.0.0.0', 12302))
        self.play_id = 0
    
    def run(self):
        while True:
            data, info = self.sock.recvfrom(65535)
            recv_Msg = data.decode()
            try:
                if recv_Msg.startswith('stop'):
                    self.stop.emit()
                elif recv_Msg.startswith('pause'):
                    self.pause.emit()
                elif recv_Msg.startswith('playid'):
                    self.play_id = int(re.findall('\d+', recv_Msg)[0])
                    self.playId()
                elif recv_Msg.startswith('play'):
                    try:
                        func, file = recv_Msg.split(",")
                        self.playFile(file)
                    except:
                        pass
                elif recv_Msg.startswith('refresh'):
                    pass
                else:
                    msg = api(recv_Msg, db)                          
                    self.udpSender.emit(msg)
                    start_new_thread(self.request_setup, (msg,))
                self.fullscreen.emit()
            except:
                self.udpSender("unknown message")

    def request_setup(self, msg):
        try:
            conn = requests.get('http://127.0.0.1:12300/setupfromplayer')
            print(conn.content)
        except:
            pass

    def playId(self):
        try:
            count = db.playlist.count_documents({})
            if self.play_id <= int(count)-1:
                file = db.playlist.find_one({'playid': self.play_id}, { 'complete_name': 1 })['complete_name']
                if os.path.isfile(file):
                    self.udpSender.emit('self.play_id,{}'.format(self.play_id))
                    self.playFile(file)
                else:
                    self.udpSender.emit('file_error')
            else:
                self.udpSender.emit('out_of_playlist_range')
        except:
            self.udpSender.emit('playid error')

    def playFile(self, mediaFile):
        try:
            file = os.path.join(MEDIA_PATH, mediaFile)
            if os.path.isfile(file):
                self.play.emit(file)
                self.udpSender.emit('play,{}'.format(mediaFile))
            else:
                self.udpSender.emit('file_error')
        except:
            self.udpSender.emit('file_error')
    
    @pyqtSlot()
    def songFinished(self):
        self.setup = db.setup.find_one({})
        if self.setup['loop_one'] == True:
            # self.stop.emit()
            self.playId()
        elif self.setup['loop'] == True:
            count = db.playlist.count_documents({})
            if self.play_id >= int(count)-1:
                self.play_id = 0
            else:
                self.play_id = self.play_id + 1
                print(self.play_id)
            self.playId()
        elif self.setup['endclose'] == True:
            self.stop.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = PlayerServer()
    sys.exit(app.exec_())