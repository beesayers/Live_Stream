# Author: Rocco Haro
# Date of creation: 04/19/2017
# retrieve_pckge_vid.py
# This script records video and converts it from .h24 to .mp4
# Saves converted video to liveStream dir

import sys
import os
import time
from threading import Thread
import pygame, sys, os
import pygame.camera
from pygame.locals import *
import subprocess
import signal
#import ffmpy
#from picamera import PiCamera
#from time import sleep
#import captureFrames


class myPiStream:
    def __init__(self):
        print("Initializing...")
        self.sleepTime = 3 # two seconds of sleeping
        self.newLaunch = True
        self.trigger = False
        self.clientCom = ""
        self.cameraLoopThread = Thread(target= self.loopControl, args=(0,))
        self.stateChangeThread = Thread(target= self.listeningForTermination, args=(0,))
        self.PAUSE = False

    def startUp(self, triggerState):
        self.newLaunch = triggerState
        self.startThreads()

    def startThreads(self):
        self.cameraLoopThread.start()
        self.stateChangeThread.start()

    def updateState(self, change):
        self.newLaunch = change

    def getTriggerStatus(self):
        return self.trigger

    def stopRecording(self, triggerInput):
         self.trigger = triggerInput

    def getClientCmd(self):
        return self.clientCom

    def clientCmd(self, triggerInput):
        self.clientCom = triggerInput

    def waitForInitiationSignal(self):
        print("Waiting for client command...")
        print("Camera is quitting.. ")
        pygame.display.quit()
        pygame.camera.quit()
        pygame.quit()

        # have RTSP socket listening here
        while True:
            response = self.getClientCmd()
            if response is "c": #triggered to continue
                print("**** retrieve_pckge_vid msg: CONTINUE REQUESTED")
                self.PAUSE = False
                self.stopRecording(False) # reset the stop recording var
                self.clientCmd("")
                self.cameraLoopThread = Thread(target= self.loopControl, args=(0,))
                self.stateChangeThread = Thread(target= self.listeningForTermination, args=(0,))
                self.startThreads()
                break
            elif response is "k":
                print("**** retrieve_pckge_vid msg: KILL REQUESTED")
                print("Goodbye")
                sys.exit()
                break
            #TODO triggered to kill

        sys.exit()

    def listeningForTermination(self, dum):
        print("Listening...")
        pause = False
        while True:
            pause = self.getTriggerStatus()
            if pause:
                print("**** retrieve_pckge_vid msg: PAUSE REQUESTED")
                self.PAUSE = True
                time.sleep(5)
                try:
                    self.cleanSnaps()
                except SystemExit:
                    pass
                print("Clean termination - comment out sys.exit to place into waiting state")
                self.waitForInitiationSignal()
                sys.exit()
        print("done listening")

    def cleanSnaps(self):
        folderToKill = "Master_Snaps"
        try:
            numFiles = len(os.listdir(folderToKill))
            cmd = "rm -rf " + folderToKill
            os.system(cmd)

            # folderToKill = '/home/rocco/Desktop/Education/Spring_17/CSCE_365/Assignments/Camera_Streaming/Testing/liveStream'
            # cmd = "rm -rf " + folderToKill
            # os.system(cmd)
            # os.makedirs("liveStream")
        except FileNotFoundError:
            print("Can not delete an absent record.")
            sys.exit()
        sys.exit()



    def backUpLiveStream(self):
        exit()
        #TODO in this function, wipe out liveStream and store to history

    def transferVidFile(self, cmd,vidFileName):
        #print("In transferVidFile")
        if not self.PAUSE:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            #os.system(cmd)

            savePath = 'liveStream/'+vidFileName
            success = False
            while not success:
                try:
                    os.rename(vidFileName , savePath)
                    success = True
                except FileNotFoundError:
                    pass
            #print("Executed transfer")
            sys.exit()
        #convert .h264 to .mp4
            # strLen = len(fileP) - 4 # distance to cut out .h264
            # newPath = fileP[:strLen]
            # newPath+= 'mp4'
            # print(newPath)
            # ff = ffmpy.FFmpeg(
            #   inputs = {'/home/pi/Desktop/liveStream/9.h264' : None},
            #    outputs = {'/home/pi/Desktop/liveStream/9.mp4': None}
            # )
            # ff.run()

    # def recordClipNum(self, index):
    #     self.camera.start_preview()
    #     filePath = '/home/pi/Desktop/liveStream/'+str(index)+'.h264'
    #     self.camera.start_recording(filePath)
    #     sleep(self.sleepTime)
    #     self.camera.stop_recording()
    #     self.camera.stop_preview()
    #
    #     self.formatVidFile(filePath)

    # def initializeCamera(self):
    #     pygame.init()
    #     pygame.camera.init()
    #
    #     # Ensure we have somewhere for the frames
    #     try:
    #         os.makedirs("Master_Snaps/Snaps0")
    #     except OSError:
    #         pass
    #
    #     self.screen = pygame.display.set_mode((1080, 1920))
    #     self.cam = pygame.camera.Camera("/dev/video0", (1080, 1920))
    #     self.cam.start()

    def convertToVid(self, folderCounter):
        if not (self.PAUSE):
            vidFileName = 'result'+str(folderCounter)+'.mp4'
            directory = 'Master_Snaps/Snaps'+str(folderCounter)
            cmd = "avconv -r 8 -f image2 -i " + directory+ "/%04d.jpg -y -qscale 0 -s 640x480 -aspect 4:3 " + vidFileName
            try:
                # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                # try:
                #     print("starting transer")
                #     self.transferVidFile(cmd)
                # except SystemExit:
                #     pass
                aThread = Thread(target = self.transferVidFile, args= (cmd,vidFileName))
                aThread.start()
                # os.sysem(cmd)
                # savePath = 'liveStream/'+vidFileName
                # os.rename(vidFileName , savePath)
                #
                # out = p.communicate()[0]
                # print(out)
                # os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                # self.loopControl(folderCounter*10)
            except SystemExit:
                pass
        sys.exit()

    def loopControl(self, counter):
        if not self.PAUSE:
            try:
                debug = False
                # self.recordClipNum(counter)
                # captureFrames.captFrames() # calls script
                # try:
                #     captureFrames.captFrames() # calls script
                # except SystemExit:
                #     print("")
                # print("In loop control")
                pygame.init()
                pygame.camera.init()
                # print("Camera initializd")
                if debug == True:
                    print("1")
                # Ensure we have somewhere for the frames
                try:
                    os.makedirs("Master_Snaps")
                except OSError:
                    print("Error in making director: Master_Snaps/Snaps0")
                    pass
                if debug == True:
                    print("2")

                screen = pygame.display.set_mode((300, 500))
                # print("Attemping to boot camera..")
                cam = pygame.camera.Camera("/dev/video0", (300, 500))
                try:
                    cam.start()
                except:
                    print("Failed to start camera")
                    exit()
                # print("Booted")
                file_num = 0
                # workingDir = 0
                done_capturing = False

                if debug == True:
                    print("3")

                while not done_capturing:
                    try:
                        image = cam.get_image()
                        screen.blit(image, (0,0))
                        pygame.display.update()
                        # Save every frame
                        filename = "Master_Snaps/" + str(file_num) + '.jpg'
                        # print(filename)
                        pygame.image.save(image, filename)
                        # if False: #file_num % 3 == 0:
                        #     #done_capturing = True
                        #     #try:
                        #         #self.convertToVid(workingDir)
                        #         #print("converted video pos: " + workingDir)
                        #     #t = Thread(target= self.convertToVid, args=(workingDir,))
                        #     #t.start()
                        #     #time.sleep(self.sleepTime)
                        #     #t.exit()
                        #     #except SystemExit:
                        #         #print("system exit from convertToVid") gets here
                        #         pass
                        #     workingDir+=1
                        #     try:
                        #         newDir = 'Snaps'+str(workingDir)
                        #         os.makedirs("Master_Snaps/"+newDir)
                        #         #print("Making new dir")
                        #         #print("Value of pause: " + str(self.PAUSE))
                        #         file_num = 0
                        #     except OSerror:
                        #         print("OS error --------")
                        #         pass
                    except:
                        print("Error saving image. Will now terminate")
                        sys.exit(1)
                    if self.PAUSE:
                        print("****** Stopped capturing")
                        cam.stop()
                        # pygame.display.quit()
                        # pygame.camera.quit()
                        # pygame.quit()
                        done_capturing = True
                    if file_num is 9999:
                        file_num = 0
                        try:
                            self.cleanSnaps()
                        except SystemExit:
                            pass
                        os.makedirs("Master_Snaps")
                    else:
                        file_num += 1
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                pass
        print("Killing loopControl")
        sys.exit(0)

        # increment counter to prepare for next clip
        # counter+=1
        #
        #
        # if (counter > 10): # under the assumption that each clip is 1 sec long,
        #     self.backUpLiveStream()  # this move onto next stage after 100 seconds
        #     self.loopControl(0) # restart loopControl with fresh counter
        # self.loopControl(counter)

x = myPiStream()