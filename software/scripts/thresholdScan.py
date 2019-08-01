#!/usr/bin/env python3
##############################################################################
## This file is part of 'ATLAS ALTIROC DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS ALTIROC DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

##############################################################################
# Script Settings

asicVersion = 1 # <= Select either V1 or V2 of the ASIC

DebugPrint = True

Configuration_LOAD_file = 'config/testBojan11.yml' # <= Path to the Configuration File to be Loaded

pixel_number = 3 # <= Pixel to be Tested

useProbe = False        #output discri probe

DataAcqusitionTOA = 1   # <= Enable TOA Data Acquisition (Delay Sweep)
NofIterationsTOA = 16  # <= Number of Iterations for each Delay value

minDAC = 360           #threshold scan
maxDAC = 380
DACstep = 1
DelayValueTOA = 0
NofIterationsTOA = 50  # <= Number of Iterations for each Delay value
LSBest = 28.64 #ch4=28.64, ch9=30.4 ch14=31.28 #ps
Qinj = 6  #Mod8.64fied Pulser Decimal code 3 = 2.66,6 = 5.24, 12 =10.32 fC, 24=20.08 fC  ##

Disable_CustomConfig = 0 # <= Disables the ASIC Configuration Customization inside the Script (Section Below) => all Configuration Parameters are taken from Configuration File   
##############################################################################

#################################################################
                                                               ##
import sys                                                     ##
import rogue                                                   ##
import time                                                    ##
import random                                                  ##
import argparse                                                ##
                                                               ##
import pyrogue as pr                                           ##
import pyrogue.gui                                             ##
import numpy as np                                             ##
import common as feb                                           ##
                                                               ##
import os                                                      ##
import rogue.utilities.fileio                                  ##
                                                               ##
import statistics                                              ##
import math                                                    ##
import matplotlib.pyplot as plt                                ##
                                                               ##
#################################################################


def set_fpga_for_custom_config(top):
    top.Asic.Probe.en_probe_pa.set(0x0)                        ##

    for i in range(25):
        top.Fpga[0].Asic.SlowControl.disable_pa[i].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_discri[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[i].set(0x1)
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.ON_Ctest[i].set(0x0)

        top.Fpga[0].Asic.SlowControl.cBit_f_TOA[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_s_TOA[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_f_TOT[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_s_TOT[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_c_TOT[i].set(0x0)

    for i in range(16):
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[i].set(0x0)

    top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.EN_hyst[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.EN_trig_ext[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.ON_Ctest[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.bit_vth_cor[pixel_number].set(0x30)

    top.Fpga[0].Asic.SlowControl.Write_opt.set(0x0)
    top.Fpga[0].Asic.SlowControl.Precharge_opt.set(0x0)

    top.Fpga[0].Asic.SlowControl.DLL_ALockR_en.set(0x1)
    top.Fpga[0].Asic.SlowControl.CP_b.set(0x5) #5
    top.Fpga[0].Asic.SlowControl.ext_Vcrtlf_en.set(0x0) #0
    top.Fpga[0].Asic.SlowControl.ext_Vcrtls_en.set(0x1) #1
    top.Fpga[0].Asic.SlowControl.ext_Vcrtlc_en.set(0x0) #0

    top.Fpga[0].Asic.SlowControl.totf_satovfw.set(0x1)
    top.Fpga[0].Asic.SlowControl.totc_satovfw.set(0x1)
    top.Fpga[0].Asic.SlowControl.toa_satovfw.set(0x1)

    top.Fpga[0].Asic.SlowControl.SatFVa.set(0x3)
    top.Fpga[0].Asic.SlowControl.IntFVa.set(0x1)
    top.Fpga[0].Asic.SlowControl.SatFTz.set(0x4)
    top.Fpga[0].Asic.SlowControl.IntFTz.set(0x1)
    
    top.Fpga[0].Asic.SlowControl.cBitf.set(0x0) #0
    top.Fpga[0].Asic.SlowControl.cBits.set(0xf) #f
    top.Fpga[0].Asic.SlowControl.cBitc.set(0xf) #f

    top.Fpga[0].Asic.SlowControl.cBit_f_TOA[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_s_TOA[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_f_TOT[pixel_number].set(0xf)  #f
    top.Fpga[0].Asic.SlowControl.cBit_s_TOT[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_c_TOT[pixel_number].set(0xf)  #f
    top.Fpga[0].Asic.SlowControl.Rin_Vpa.set(0x1) #0
    top.Fpga[0].Asic.SlowControl.cd[0].set(0x0) #6
    top.Fpga[0].Asic.SlowControl.dac_biaspa.set(0x10) #10
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(0x7) #7
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(0x19f) #173 / 183

    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(0x0)   # Rising edge of EXT_TRIG or CMD_PULSE delay
    top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(0xfff) # Falling edge of EXT_TRIG (independent of CMD_PULSE)

    top.Fpga[0].Asic.Readout.StartPix.set(pixel_number)
    top.Fpga[0].Asic.Readout.LastPix.set(pixel_number)

#################################################################


#################################################################
# Set the argument parser
parser = argparse.ArgumentParser()

# Convert str to bool
argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']

# Add arguments
parser.add_argument(
    "--ip", 
    nargs    ='+',
    required = True,
    help     = "List of IP addresses",
)  

parser.add_argument(
    "--out",
    type = str,
    required = False,
    default = 'testThreshold.txt',
    help = "output file name")  

# Get the arguments
args = parser.parse_args()

#################################################################
# Setup root class
top = feb.Top(ip= args.ip)    

# Load the default YAML file
print(f'Loading {Configuration_LOAD_file} Configuration File...')
top.LoadConfig(arg = Configuration_LOAD_file)

if DebugPrint:
    # Tap the streaming data interface (same interface that writes to file)
    dataStream = feb.MyEventReader()    
    pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA

# Custom Configuration
if Disable_CustomConfig == 0:
    set_fpga_for_custom_config(top)


#################################################################
# Data Stream Alignment                                        ##
                                                               ##
top.Asic.PulseTrain.Continuous.set(0x0)                        ##
top.Asic.Gpio.RSTB_TDC.set(0x0)                                ##
Write_opt = top.Asic.SlowControl.Write_opt.get()               ##
Precharge_opt = top.Asic.SlowControl.Precharge_opt.get()       ##  
top.Asic.SlowControl.Write_opt.set(0x0)                        ##
top.Asic.SlowControl.Precharge_opt.set(0x0)                    ##
time.sleep(0.1)                                                ##
top.Asic.PulseTrain.ResetCounterPolarity.set(0x1)              ##
top.Asic.PulseTrain.Continuous.set(0x1)                        ##
time.sleep(0.1)                                                ##
top.Asic.SlowControl.Write_opt.set(Write_opt)                  ##
top.Asic.SlowControl.Precharge_opt.set(Precharge_opt)          ##
top.Asic.Gpio.RSTB_TDC.set(0x1)                                ##
top.Asic.PulseTrain.ResetCounterPolarity.set(0x0)              ##
top.Asic.PulseTrain.Continuous.set(0x0)                        ##
time.sleep(0.1)                                                ##
#################################################################

#################################################################
# Data Acquisition                                             ##
# vs threshold                                                 ##
dacScan = []                                                   ##
                                                               ##
for i in range(minDAC,maxDAC,DACstep):                         ##
                                                               ##
    print ('ThresholdDAC =',i)                                 ##
    dacScan.append(i)                                          ##
    top.Asic.SlowControl.DAC10bit.set(i) #350                  ##
    ##align data after each thr setting?                       ##
                                                               ##
    try:                                                       ##
        os.remove('TestData/test_th%d.dat' %i)                 ##
    except OSError:                                            ##
        pass                                                   ##

    top.dataWriter._writer.open('TestData/test_th%d.dat' %i)   ##
    top.Asic.DoutDebug.ForwardData.set(0x1)                    ##
    time.sleep(0.1)
    for j in range(NofIterationsTOA):                          ##
        top.Asic.Gpio.RSTB_TDC.set(0x0)                        ##
        top.Asic.Gpio.RSTB_TDC.set(0x1)                        ##
        time.sleep(0.01)                                       ##
        top.Asic.PulseTrain.OneShot()                          ##
                                                               ##
    top.Asic.DoutDebug.ForwardData.set(0x0)                    ##
    top.dataWriter._writer.close()                             ##
                                                               ##
#################################################################

#################################################################
# Data Processing

thr_DAC = []
HitCnt = []
TOAmean = []
TOAjit = []
TOAmean_ps = []
TOAjit_ps = []

for i in dacScan:
    # Create the File reader streaming interface
    dataReader = rogue.utilities.fileio.StreamReader()
    time.sleep(0.01)
    # Create the Event reader streaming interface
    dataStream = MyFileReader()
    time.sleep(0.01)
    # Connect the file reader to the event reader
    pr.streamConnect(dataReader, dataStream) 
    time.sleep(0.01)
    # Open the file
    dataReader.open('TestData/test_th%d.dat' %i)
    time.sleep(0.01)
    # Close file once everything processed
    dataReader.closeWait()
    time.sleep(0.01)

    try:
        print('Processing Data for THR DAC = %d...' % i)
    except OSError:
        pass 

    HitData = dataStream.HitData

    thr_DAC.append(i)
    HitCnt.append(len(HitData))
    if len(HitData) > 0:
        TOAmean.append(np.mean(HitData, dtype=np.float64))
        TOAjit.append(math.sqrt(math.pow(np.std(HitData, dtype=np.float64),2)+1/12))
        TOAmean_ps.append(np.mean(HitData, dtype=np.float64)*LSBest)
        TOAjit_ps.append(math.sqrt(math.pow(np.std(HitData, dtype=np.float64),2)+1/12)*LSBest)

    else:
        TOAmean.append(0)
        TOAjit.append(0)
        TOAmean_ps.append(0)
        TOAjit_ps.append(0)
 
#################################################################

#################################################################
# Print Data
#find min th, max th, and middle points:
minTH = 0.
maxTH = 1024.
th50percent = 1024.

midPt = []
for i in range(len(dacScan)):
    try:
        print('Threshold = %d, HitCnt = %d/%d' % (dacScan[i], HitCnt[i], NofIterationsTOA))
    except OSError:
        pass
    if HitCnt[i] == NofIterationsTOA:
        if i>0 and HitCnt[i-1] > NofIterationsTOA :
            minTH = (dacScan[i-1]+dacScan[i])/2
        elif i<len(dacScan)-1 and HitCnt[i+1] < NofIterationsTOA :
            maxTH = (dacScan[i+1]+dacScan[i])/2
    if HitCnt[i]/NofIterationsTOA < 0.6:
        th50percent = dacScan[i]

th25= (maxTH-minTH)*0.25+minTH
th50= (maxTH-minTH)*0.5+minTH
th75= (maxTH-minTH)*0.75+minTH
print('Found minTH = %d, maxTH = %d  - points at 0.25, 0.50 and 0.75 are %d,%d,%d'% (minTH,maxTH,th25,th50,th75))
print('First DAC with efficiency below 60% = ', th50percent)
ff = open(args.out,'a')
ff.write('Threshold scan ----'+time.ctime()+'\n')
ff.write('Pixel = '+str(pixel_number)+'\n')
#ff.write('column = '+hex(column)+'\n')
ff.write('config file = '+Configuration_LOAD_file+'\n')
ff.write('NofIterationsTOA = '+str(NofIterationsTOA)+'\n')
#ff.write('dac_biaspa = '+hex(dac_biaspa)+'\n')
ff.write('cmd_pulser = '+str(Qinj)+'\n')
ff.write('LSBest = '+str(LSBest)+'\n')
#ff.write('Cd ='+str(cd*0.5)+' fC'+'\n')
ff.write('Found minTH = %d, maxTH = %d - points at 0.25, 0.50 and 0.75 are %d,%d,%d \n'% (minTH,maxTH,th25,th50,th75))
ff.write('First DAC with efficiency below 0.6 = %d  \n' % (th50percent))
ff.write('Threshold = '+str(dacScan)+'\n')
ff.write('N hits = '+str(HitCnt)+'\n')
ff.write('Mean TOA = '+str(TOAmean)+'\n')
ff.write('Std Dev TOA = '+str(TOAjit)+'\n')
ff.write('MeanTOAps = '+str(TOAmean_ps)+'\n')
ff.write('StdDevTOAps = '+str(TOAjit_ps)+'\n')
ff.write('\n')
ff.close()

#################################################################
#################################################################
## Plot Data
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))

#plot N events vs threshold
ax1.plot(dacScan,HitCnt)
#ax1.scatter(dacScan,HitCnt)
ax1.set_title('Number of hits vs Threshold', fontsize = 11)

#plot TOA vs threshold
ax2.scatter(dacScan,TOAmean_ps)
ax2.set_title('Mean TOA vs Threshold', fontsize = 11)

#plot jitter vs Threshold
ax3.scatter(dacScan,TOAjit_ps)
ax3.set_title('Jitter TOA vs Threshold', fontsize = 11)

plt.subplots_adjust(hspace = 0.35, wspace = 0.2)
plt.show()
#################################################################

time.sleep(0.5)
# Close
top.stop()
