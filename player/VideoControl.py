#!/usr/bin/env python
import sys
import os
import socket
import vlc
from time import sleep
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QThread

global videoFileName

class MyWindow(QWidget):
    tcpServerReturnString = pyqtSignal(str)
    player_State = pyqtSignal(str)
    player_play = pyqtSignal(str)
    player_pause = pyqtSignal()
    player_stop = pyqtSignal()
    player_getTime = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        global videoFileName
        self.setGeometry(100, 200, 300, 100)
        self.setWindowTitle("Video Player Remote")
        self.pushButton = QPushButton("File Open")
        self.pushButton.clicked.connect(self.pushButtonClicked)
        self.label = QLabel()
        self.label_Help = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.pushButton)
        layout.addWidget(self.label)
        layout.addWidget(self.label_Help)
        self.setLayout(layout)
        self.show()

        self.label_Help.setText('TCP Port = 12303\nProtocol\nplay\nplay,[FileName]\nstop')

        self.TcpSoketServer = TCPServer_Socket()
        self.audioStreamReceiver = audioStreamReceiver()
        self.TcpSoketServer.TCPServerReceiveString.connect(self.server_data_parcing)
        self.tcpServerReturnString.connect(self.TcpSoketServer.stringReturn)
        self.audioStreamReceiver.player_State.connect(self.TcpSoketServer.stringReturn)
        self.player_play.connect(self.audioStreamReceiver.playStream)
        self.player_pause.connect(self.audioStreamReceiver.pauseStream)
        self.player_stop.connect(self.audioStreamReceiver.stopStream)
        self.player_getTime.connect(self.audioStreamReceiver.getTime)
        self.TcpSoketServer.start()

        try:
            with open('selfile.list','r') as file:
                filenameloaded = file.read().splitlines()
                videoFileName = filenameloaded[0]
                self.label.setText(videoFileName)
        except:
            pass

    def pushButtonClicked(self):
        global videoFileName
        fname = QFileDialog.getOpenFileName(self)
        videoFileName = fname[0]
        self.label.setText(videoFileName)
        try:
            with open('selfile.list','w') as file:
                file.write(videoFileName+'\n')
        except:
            pass

    #Server Data Parcing
    @pyqtSlot(str)
    def server_data_parcing(self,data):
        global videoFileName
        try:
            if data == 'play':
                self.player_play.emit(videoFileName)
            elif data == 'stop':
                stopVal = 1
                self.player_stop.emit()
            elif data == 'pause':
                self.player_pause.emit()
            elif data == 'gettime':
                self.player_getTime.emit()
            else:
                playlist = data.split(',')
                if playlist[0] == 'play':
                    self.player_play.emit(playlist[1])
                else:
                    self.tcpServerReturnString.emit('File Name Error')
        except:
            self.tcpServerReturnString.emit('File Name Error')

#TCP서버 클래스
class TCPServer_Socket(QThread):
    TCPServerReceiveString = pyqtSignal(str)
    def __init__(self, parent = None):
        super(TCPServer_Socket, self).__init__(parent)
        self.server_client = None
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_socket.bind(("",12303))
        self.server_socket.listen(5)

    #Tcp Server Start
    def run(self):
        while True:
            try:
                if self.server_client is None:
                    print('Waiting for Client')
                    self.server_client, addr = self.server_socket.accept()
                    print("Clinet Connect : ", addr)
                    self.server_client.send('Connected Player'.encode('utf-8'))

                else:
                    print("Waiting for response...")
                    self.receiveData = self.server_client.recv(1024)
                    self.receiveData = self.receiveData.decode('utf-8')
                    if self.receiveData == "":
                        break
                    else:
                        self.TCPServerReceiveString.emit(self.receiveData)
            except socket.error as e:
                print("Server Socket error {0} reconncting".format(e))
                break
        self.serverReStart()

    #TCP Server Return
    @pyqtSlot(str)
    def stringReturn(self, data):
        if self.server_client != None:
            self.server_client.send(data.encode('utf-8'))

    #TCP Server Restart
    def serverReStart(self):
        sleep(0.1)
        self.server_client = None
        self.run()

class audioStreamReceiver(QThread):
    player_State = pyqtSignal(str)
    play_on = pyqtSignal(bool)
    def __init__(self, parent = None):
        super(audioStreamReceiver, self).__init__(parent)
        self.player = None

    @pyqtSlot(str)
    def playStream(self, playlist_rt):
        if self.player == None:
            try:
                print("{}".format(playlist_rt))
                self.instance = vlc.Instance(['--video-on-top'])
                self.player = self.instance.media_player_new()
                self.player.set_fullscreen(True)
                #sleep(.5)
                self.media = self.instance.media_new(playlist_rt)
                self.currentMedia = playlist_rt
                self.player.set_media(self.media)
                self.player.play()
                sleep(.5)
                self.duration = self.player.get_length()/1000
                self.mm,self.ss = divmod(self.duration, 60)
                self.mm = round(self.mm)
                self.ss = round(self.ss)
                self.player_State.emit('Play Start Length {}m,{}s'.format(self.mm,self.ss))
            except:
                print('Play Media Error')
                self.player = None
                self.player_State.emit('Player Error')
        else:
            if self.currentMedia != playlist_rt:
                self.currentMedia = playlist_rt
                self.media = self.instance.media_new(playlist_rt)
                self.player.set_media(self.media)
                self.player.play()
                sleep(.5)
                self.duration = self.player.get_length()/1000
                self.mm,self.ss = divmod(self.duration, 60)
                self.mm = round(self.mm)
                self.ss = round(self.ss)
                self.player_State.emit('Play Start Length {}m,{}s'.format(self.mm,self.ss))
            
    @pyqtSlot()
    def pauseStream(self):
        if self.player == None:
            print('No Media')
            self.player_State.emit('Player NoMedia')
        else:
            self.player.pause()
            print(self.player.get_state())
            self.player_State.emit('Paused')

            self.duration = self.player.get_time()/1000
            self.mm,self.ss = divmod(self.duration, 60)
            self.mm = round(self.mm)
            self.ss = round(self.ss)
            self.player_State.emit('Time {}m,{}s'.format(self.mm,self.ss))

    @pyqtSlot()
    def getTime(self):
        if self.player == None:
            print('No Media')
            self.player_State.emit('Player NoMedia')
        else:
            self.duration = self.player.get_time()/1000
            self.mm,self.ss = divmod(self.duration, 60)
            self.mm = round(self.mm)
            self.ss = round(self.ss)
            self.player_State.emit('Time {}m,{}s'.format(self.mm,self.ss))
            print('Playtime {}m,{}s'.format(self.mm,self.ss))
            
    @pyqtSlot()
    def stopStream(self):
        if self.player != None:
            self.player.stop()
        self.player = None
        self.player_State.emit('Player Stop')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MyWindow()
    sys.exit(app.exec_())