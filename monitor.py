from ROOT import TH1, TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TGraph
from array import array
import numpy as np
from ROOT import THttpServer
import argparse
import threading
import ROOT
import os
import time as t

import header as h
import tasks as task
import ratePlots as r
import hitPlots as hit
import hitMaps as map
import luminosity as lum
import reader as read
import valuePlots as val
import timeAlign as align

#default arguments in header, should be edited as they become parsed arguments
#add arguments for runNumber and dataNumber
parser = argparse.ArgumentParser()
parser.add_argument('runNumber', type=str)
parser.add_argument('fileNumber', type=str)
parser.add_argument('serverNumber',type=str)
parser.add_argument('beammode',type=str)
args = parser.parse_args()

h.fileN = int(args.fileNumber)
h.runN = int(args.runNumber)

#make run (file) number 6 (4) digits , 0 padded
runNumber = args.runNumber.rjust(6,"0")
fileNumber = args.fileNumber.rjust(4,"0")
serverNumber = args.serverNumber.rjust(4,"0")
beammode = args.beammode.lower()
print(f"Beammode = {beammode} --------------------------",flush=True)


h.filedir = f"root://snd-server-1:1094///mnt/raid1/data_online/" #online
#h.filedir = f"/home/sndmon/QtDqmp/Data/"   #local new
#h.filedir = f"/home/sndmon/Snd/Data/"   #local old
#h.filedir = f"/home/sndecs/RunData/" #local TB

h.filename = h.filedir + f"run_{runNumber}/data_{fileNumber}.root"

h.wrtfile = ROOT.TFile.Open(h.wrtfilename, "RECREATE")
print(f"creating write file: {h.wrtfilename}",flush=True)
h.wrtfile.Close()

h.file = ROOT.TFile.Open(h.filename,'r')
print(f"opening file first time: {h.filename}",flush=True)

task.setBeamParam(beammode)

#avoid segmentation violation when closing file
#TH1.AddDirectory(False)

#run through all the events (best for complete files)
task.updateAllEvents()

#h.plotWholeRate = True

#start from the event arg1 seconds ago, until h.timeRange
#task.updateSecondsAgo(5)

#plot events between arg1 and arg2 seconds ago
#task.updateTimeRange(240,120)

#enable root multithreading   
nThreads = 6
ROOT.EnableThreadSafety()
ROOT.EnableImplicitMT(nThreads)

print("To kill program, enter Ctrl+\\",flush=True)

#gROOT.SetBatch(True)

#load server
#go to zh-desktop:710X?top=monitoring
#serverName = f"http:{serverNumber}?top=monitoring"
#serv = THttpServer(serverName)
#serv.CreateServerThread()
#serv.Register("Graphs",h.wrtfile)

#serv.CreateEngine("fastcgi:9000")

#pull board info from json file
task.getBoardArrays(beammode)

#define threading functions
reader = threading.Thread(target=read.readEntry)
rate = threading.Thread(target=r.plotGlobalEvtRate)
lumi = threading.Thread(target=lum.main)

rateVeto = threading.Thread(target=r.plotDetEvtRate, args = ("Veto",h.vetoId))
rateSciFi = threading.Thread(target=r.plotDetEvtRate, args=("Scifi",h.sciFiId))
rateUS = threading.Thread(target=r.plotDetEvtRate, args=("US",h.usId))
rateDS   = threading.Thread(target=r.plotDetEvtRate, args=("DS",h.dsId))
rateBM = threading.Thread(target=r.plotDetEvtRate, args=("BM",h.beammonId))

sciFiCh = threading.Thread(target=hit.plotHitsChDet, args=("SciFi",h.sciFiId,h.sciFiName))
vetoCh = threading.Thread(target=hit.plotHitsChannel, args=("Veto",h.vetoId))
usCh = threading.Thread(target=hit.plotHitsChDet, args=("US",h.usId,h.usName))
dsCh = threading.Thread(target=hit.plotHitsChDet, args=("DS",h.dsId,h.dsName))
BMCh = threading.Thread(target=hit.plotHitsChDet, args=("BM",h.beammonId,h.beammonName))

hitsTot = threading.Thread(target=hit.plotHitsBoard, args=("Total",h.totId,h.totName))
hitsSciFi = threading.Thread(target=hit.plotHitsBoard, args=("SciFi",h.sciFiId,h.sciFiName))
hitsUS = threading.Thread(target=hit.plotHitsBoard, args=("US",h.usId,h.usName))
hitsDS = threading.Thread(target=hit.plotHitsBoard, args=("DS",h.dsId,h.dsName))
hitsBM = threading.Thread(target=hit.plotHitsBoard, args=("BM",h.beammonId,h.beammonName))

hitMap = threading.Thread(target=map.plot2DMap, args=(24,53,[0,1,2,3,5,6,7],[0,1,2,3,5,6,7],"SciFi_1_hitmap",1,1))
valDS = threading.Thread(target=val.plotValueBoard, args=("DS",h.dsId))
valUS = threading.Thread(target=val.plotValueBoard, args=("US",h.usId))
alignUS = threading.Thread(target=align.plotTimeAlign, args=("US",h.usId))

planeUS = threading.Thread(target=hit.plotHitsPlane, args=("US",h.usId,h.usPName, h.usSlot))
planeDS = threading.Thread(target=hit.plotHitsPlane, args=("DS",h.dsId,h.dsPName, h.dsSlot))


reader.start()   # must be always active

#start threads

print(h.usId)
print(h.usName)
print(h.usPName)
print(h.usSlot)

print(h.sciFiId)
print(h.sciFiName)
print(h.sciFiPName)
print(h.sciFiSlot)


#rateVeto.start() 
#rateSciFi.start() 
#rateUS.start()
#rateDS.start()
#rateBM.start()
  
#hitsTot.start()
#hitsSciFi.start()
#hitsUS.start()
#hitsDS.start()
#hitsBM.start()

#vetoCh.start()
#sciFiCh.start()             
#usCh.start()
#dsCh.start()
#BMCh.start() 

#hitMap.start()
#valDS.start()
#valUS.start()
#alignUS.start()

#planeUS.start()
planeDS.start()

#if args.beammode == 'STABLE':
lumi.start()

#rate should ALWAYS be running!
rate.start()

while(True):
    if (gSystem.ProcessEvents()):
        break
