# -*- coding: utf-8 -*-
import sys, vlc, socket, os.path, threading, json, re, requests, json
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

playlist_id = 0
current_playlist = []
playlistGroup = []
for i in range(8):
    playlistGroup.append(db['playlist_{}'.format(i)])
setup = db['setups']
filelist = db['filelists']

class PlayerServer(QVideoWidget):
    songFinishedEvent = pyqtSignal()
    def __init__(self):
        super().__init__()        
        self.setupUI()
        self.playlist = None
        self.mediafile = None
        self.curr_time = None
        self.duration = None
        self.playlist_id = None
        self.fullscreenCurrent = False
        self.udpServer = udpServer()
        self.udpServer.start()

        self.udpServer.play.connect(self.play)
        self.udpServer.stop.connect(self.stop)
        self.udpServer.pause.connect(self.pause)
        self.udpServer.fullscreen.connect(self.fullscreen)
        self.udpServer.udpSender.connect(self.udpSender)
        self.songFinishedEvent.connect(self.udpServer.songFinished)

        self.mc_grp = '230.128.128.128'
        self.mc_port = 12345
        self.mc_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.mc_sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        self.setNewPlayer()
        self.show()

        self.setup = setup.find_one({})
        print (self.setup)
        try:
            if self.setup['fullscreen'] == True:
                self.fullscreen()
                self.fullscreenCurrent = True
            else:
                self.fullscreenCurrent = False

            if self.setup['poweronplay'] == True:
                file = playlistGroup[playlist_id].find_one({'playid': 0}, { 'complete_name': 1 })['complete_name']
                # sleep(5)
                self.play(file)
        except:
            pass

    def setupUI(self):
        self.setWindowTitle("MEDIA SERVER")
        self.setWindowIcon(QIcon('favicon_player.ico'))
        self.setStyleSheet("background-color: white;")
        self.logo = QLabel(self)
        self.pix = QPixmap()
        self.pix.load("logo.png")
        self.pix = self.pix.scaledToWidth(600)
        self.logo.setPixmap(self.pix)
        self.logo.setAlignment(Qt.AlignCenter)

        self.h_box = QHBoxLayout(self)
        self.v_box = QVBoxLayout()
        self.h_box.addLayout(self.v_box)
        self.v_box.addWidget(self.logo)

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
        self.udpSendSock.sendto(msg.encode('utf-8'), (self.setup['rtIp'], self.setup['rtPort']))
        self.udpSendSock.close()
    
    def setMedia(self, mediaFile):
        self.media = self.instance.media_new(mediaFile)
        self.player.set_media(self.media)

    @pyqtSlot(str)
    def play(self, mediaFile):
        if self.mediafile == mediaFile: self.player.stop()
        else: self.mediafile = mediaFile; self.setMedia(mediaFile)
        rtjson = { 'playlist': playlist_id, 'playfile': os.path.basename(mediaFile) }
        self.mc_sender.sendto(json.dumps(rtjson).encode('utf-8'), (self.mc_grp, self.mc_port))
        self.player.play()
        self.fullscreen()

    @pyqtSlot()
    def pause(self):
        self.player.pause()

    @pyqtSlot()
    def stop(self):
        self.player.stop()
        rtjson = { 'stop': True }
        self.mc_sender.sendto(json.dumps(rtjson).encode('utf-8'), (self.mc_grp, self.mc_port))
        self.mediafile = None

    @pyqtSlot()
    def fullscreen(self):
        self.setup = setup.find_one({})
        if self.fullscreenCurrent != self.setup['fullscreen']:
            self.setFullScreen(self.setup['fullscreen'])
            self.fullscreenCurrent = self.setup['fullscreen']

    def songFinished(self,evnet):
        self.songFinishedEvent.emit()
        rtjson = { 'stop': True }
        self.mc_sender.sendto(json.dumps(rtjson).encode('utf-8'), (self.mc_grp, self.mc_port))

    def getMediaLength(self, time, player):
        sendTime = timeFormat(time.u.new_length)
        if self.duration != sendTime:
            self.duration = sendTime
            start_new_thread(self.udpSender, ('length,{}'.format(sendTime),))

    def getCurrentTime(self, time, player):
        start_new_thread(self.currentTimeProcess, (time,))
    
    def currentTimeProcess(self, time):
        sendTime = timeFormat(time.u.new_time)
        if self.curr_time != sendTime:
            self.curr_time = sendTime
            rtjson = { 'duration': sendTime }
            self.mc_sender.sendto(json.dumps(rtjson).encode('utf-8'), (self.mc_grp, self.mc_port))
            if self.setup['progress']:
                self.udpSender('current,{}'.format(sendTime))


class udpServer(QThread):
    play = pyqtSignal(str)
    stop = pyqtSignal()
    pause = pyqtSignal()
    fullscreen = pyqtSignal()
    udpSender = pyqtSignal(str)
    playlist_id = pyqtSignal(int)

    def __init__(self, parent = None):
        super(udpServer, self).__init__(parent)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        print("Udp Server Start {} : {}".format('0.0.0.0', 12302))
        self.play_id = 0
    
    def run(self):
        global playlist_id, current_playlist
        while True:
            data, info = self.sock.recvfrom(65535)
            recv_Msg = data.decode()
            print(recv_Msg)
            try:
                if recv_Msg.startswith('stop'):
                    self.stop.emit()
                elif recv_Msg.startswith('pause'):
                    self.pause.emit()
                elif recv_Msg.startswith('fullscreen'):
                    self.fullscreen.emit()
                elif recv_Msg.startswith('pi,'):
                    pi = recv_Msg.split(",", 2)
                    playlist_id = int(pi[1])
                    self.play_id = int(pi[2])
                    current_playlist = (list(playlistGroup[playlist_id].find()))
                    self.playId()
                elif recv_Msg.startswith('pl,'):
                    pl = recv_Msg.split(",", 1)
                    playlist_id = int(pl[1])
                    self.play_id = 0
                    current_playlist = (list(playlistGroup[playlist_id].find()))
                    self.playId()
                elif recv_Msg.startswith('p,'):
                    func, file = recv_Msg.split(",")
                elif recv_Msg.startswith('refresh'):
                    pass
                else:
                    msg = api(recv_Msg, setup, playlistGroup, filelist)                          
                    self.udpSender.emit(msg)
                    self.fullscreen.emit()
                    # start_new_thread(self.request_setup, (msg,))
                
            except:
                self.udpSender("unknown message")

    def request_setup(self, msg):
        try:
            conn = requests.get('http://127.0.0.1:3000/setupfromplayer')
            print(conn.content)
        except:
            pass

    def playId(self):
        global current_playlist
        try:
            count = len(current_playlist)
            if self.play_id <= int(count)-1:
                file = current_playlist[self.play_id]["complete_name"]
                
                if os.path.isfile(file):
                    self.udpSender.emit('play:pl,id:{},list:{}'.format(self.play_id, playlist_id))
                    self.playFile(file)
                else:
                    self.udpSender.emit('err:none_file')
            else:
                self.udpSender.emit('err:outofrange')
        except:
            self.udpSender.emit('err:player_err')

    def playFile(self, mediaFile):
        try:
            file = os.path.join(MEDIA_PATH, mediaFile)
            if os.path.isfile(file):
                self.play.emit(file)
                self.udpSender.emit('play:p,file:{}'.format(mediaFile))
            else:
                self.udpSender.emit('err:none_file')
        except:
            self.udpSender.emit('err:player_err')
    
    @pyqtSlot()
    def songFinished(self):
        self.setup = setup.find_one({})
        if self.setup['loop_one'] == True:
            # self.stop.emit()
            self.playId()
            self.udpSender.emit("playid,{}".format(self.play_id))
        elif self.setup['loop'] == True:
            count = len(current_playlist)
            if self.play_id >= int(count)-1:
                self.play_id = 0
            else:
                self.play_id = self.play_id + 1
                print(self.play_id)
            self.playId()
            self.udpSender.emit("playid,{}".format(self.play_id))
        elif self.setup['endclose'] == True:
            self.stop.emit()
            self.udpSender.emit("stop:true")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = PlayerServer()
    sys.exit(app.exec_())