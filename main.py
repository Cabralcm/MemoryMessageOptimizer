#!/usr/bin/env python

import os
import subprocess
import sys
import datetime
import pandas as pd
import numpy as np
import math
import csv
import ast
import re
import argparse
import shutil
import heapq
import matplotlib.pyplot as plt
from matplotlib import rcParams


from Tkinter import *
import ttk
import tkMessageBox
import tkFileDialog


#########################################################################
###   ReadMe                                                            #
#########################################################################
'''
Original text removed.

Memory Matrix: 200 x 336
200 rows, by 336 columns (length of row)
'''

#Version 0.89
global_version = 0.90
#Jan 08, 2019
#Christopher Cabral

#########################################################################
#  Parameters                                                           #
#########################################################################

#####################################################################################
#Memory Space Parameters                                                            #
#####################################################################################
ref_val = 336
row_limit = 200

#####################################################################################
#Independent File ORDER Analysis and Optimization                                   #
#If = 1, file independent order                                                     #
#If = 0, use "MSG_file_order" array to determine file order                         #
#####################################################################################
file_independent = 1

#####################################################################################
#Separate File Message Analysis and Optimization                                    #
# If = 1, independent msg analysis (calc optimization each MSG file independently)  #
# If = 0, calculate optimization for all MSG files as a group                       #
#####################################################################################
message_independent = 1

####################################################################################
#Automatically generate MSG Files with the Optimized Alarm Messages incorporated   #
#If = True, automatically generate MSG files with Optimized Alarm Messages         #
#If = anything else, do not generate MSG Files                                     #
####################################################################################
automatic_MSG_output = None

#####################################################################################
#Graph Output - Automation                                                          #
#If = True, automatically save output graph                                         #
#If = Anything else, need to manually save output graph                             #
#####################################################################################
automatic_graph_output = True

#####################################################################################
# Input Directory                                                                   #
#####################################################################################
input_directory = r"C:\Users\Chris Laptop\Desktop\MSG"
hard_coded_input_directory = input_directory
#cwd = "./"

#####################################################################################
#Python Alarm Output Directory                                                      #
#####################################################################################
#python_output_directory = "./Alarm Message Output"
python_output_directory =  os.getcwd() + "\Alarm Message Output"
hard_coded_python_output_directory = python_output_directory

#####################################################################################
#Python MSG and TEMP file directories                                               #
#####################################################################################
MSG_output_directory = python_output_directory + "/MSG/"    #These MSG blueprint files with Alarm messages optimized
temp_MSG_output_directory = MSG_output_directory + "TEMP/"  #These are copies of the production files, to be read from

#####################################################################################
#File to write suggested Message Order to and Message File Parameters               #
#####################################################################################
message_file = python_output_directory + "/Suggested Message Order.txt"

message_file_header = """*** Alarm Message File Optimizer *** \n
This file provides a SUGGESTED ORDER for Alarm Messages which may improve
quality of message compression in Messages Buffer. This order is
merely a suggestion, those writing Message code should test and verify all code
for themselves. Moreover, this optimization does not account for: human
readability of code, such as order or strategically placed comments around
messages.
\nCurrent storage capacity of buffer is set to: """ + str(ref_val) + " x " + str(row_limit) + " , that is: (row length) x (number of rows)"

new_file_header = "--------------------------------------------------------------------------------------------------"
message_block_separator = "*** Start of Message Block ***"

#####################################################################################
#Option to Write to Suggested Message File                                          #
#True = create and write to the message file                                        #
#False = do not write to the message file                                           #
#####################################################################################
write_message_file = True

#####################################################################################
#Option to Turn Off creating MSG Blueprint files with Alarm Messages optimized      #
#True = create the 20 blueprint alarm message files                                 #
#False = do not create the 20 blueprint alarm message files                         #
#####################################################################################
write_MSG_files = True

#####################################################################################
#Input and Output file lists                                                        #
#####################################################################################
input_file_list = "/Input_File_List.csv"
output_file_list = "/Output_File_List.csv"

generate_input_file_list = False
generate_output_file_list = False

#####################################################################################
#MSG Message Order in SCADA File Upload                                             #
#####################################################################################
#MSG_file_order is the default list as of the time of this script being written: Jan 17, 2019
#This list can be changed, but make sure that it is in the form of a list/array,
#with each element being the name of the MSG file in the desired file order in which it is processed in SCADA


# Filler file names have been substituted. 
MSG_file_order = ["File1", "File2", "File3", "File4", "File5",
                  "File6", "File7", "File8", "File9", "File10",
                  "File11", "File12", "File13", "File14", "File15",
                  "File16", "File17", "File18", "File19", "File20"
                  ]

hard_coded_MSG_file_order = MSG_file_order
display_MSG_file_order = MSG_file_order

#####################################################################################
#MSG Message Order - Configuration File                                             #
#User-written list the MSG file order (supposed to match the order in SCADA)        #
#####################################################################################
config_file_name = "config.txt" #Make sure you include .txt for the file
use_config_file = False

start_of_list_flag = "***MSG FILE ORDER START***"

end_of_list_flag = "***MSG FILE ORDER END***"

#########################################################################
# End of Parameters                                                     #
#########################################################################

#########################################################################
# Static Configurations (Do not change)                                 #
#########################################################################

#Set Parameter for MatPlotLib
rcParams.update({'figure.autolayout': True})

#########################################################################
# End of Static Configurations (Do not change)                          #
#########################################################################

'''
#Attempt at more elemgant MinHeap (work in progress, and not tested)
class MinHeap:
    def __init__(self):
        self.heap = []
        
    def push(self, item):
        heapq.heappush(self.heap, item)

    def pop(self):
        return heapq.heappop(self.heap)

    def peak(self):
        return self.heap[0][0]

    def __getitem__(self,item):
        return self.heap[item]

    def __len__(self):
        return len(self.heap)

    
class MaxHeap(MinHeap):
    def push(self,item):
        heapq.heappush(self.heap, Comparator(item))

class Comparator:
    def __init__(self, val):
        self.val = val
    def __lt__(self, other):
        return self.val > other.val
    def __le__(self,other):
        return self.val >= other.val
    def __gt__(self,other):
        return self.val < other.val
    def __ge__(self,other):
        return self.val <= other.val
    def __eq__(self,other):
        return self.val == other.val
    def __ne__(self,other):
        return self.val != other.val   
'''
#####################################################################################
#General Function Scripts to set-up global variables and configuration files        #
#####################################################################################

def check_config_file():
    global config_file_name
    global use_config_file

    cwd = os.getcwd()
    config_file = cwd + "\\" + config_file_name

    for eachFile in os.listdir(cwd):
        file_path = os.path.join(cwd, eachFile)
        if os.path.isfile(file_path):
            if(config_file == file_path):
                use_config_file = True
                break
    return

def read_config_file():
    global use_config_file
    global config_file_name
    global MSG_file_order
    global start_of_list_flag
    global end_of_list_flag
    
    if(use_config_file == True):        
        cwd = os.getcwd()
        config_file = cwd + "\\" + config_file_name

        list_flag = 0
        MSG_file_order_array = []
        
        input_file = open(config_file_name, "r")
        for num, line in enumerate(input_file):
            if ((list_flag == 0) and (start_of_list_flag in line)):
                list_flag = 1
                continue
            elif((list_flag == 1) and (end_of_list_flag in line)):
                list_flag = 2
                break
            elif(list_flag == 1):
                MSG_file_order_array.append(line)
                continue

        #Close Configuration File
        input_file.close()
        
        #Remove white-space characters
        MSG_file_order_array = [element.strip() for element in MSG_file_order_array]

        #Set MSG File Order
        MSG_file_order = MSG_file_order_array        
    return

def format_MSG_file_order():
    global MSG_file_order
    global display_MSG_file_order
    output_string = ""
    for element in MSG_file_order[:-1]:
        output_string += element +", "

    output_string += MSG_file_order[-1]

    display_MSG_file_order = output_string
    return     

#####################################################################################
#END OF General Function Scripts to set-up global variables and configuration files #
#####################################################################################       

#####################################################################################
#General Function Scripts - Function Calls                                          #
#####################################################################################

#Check if configuration file exists. If exists, sets: use_config_file = True
check_config_file()

#If configuration file exists, set "MSG_file_order" List to Configuration File's List
read_config_file()

#Format MSG_file_order Array into a string for visual appeal in GUI
format_MSG_file_order()
#####################################################################################
#END OF General Function Scripts - Function Calls                                   #
#####################################################################################

#Custom built MaxHeap for array where each element is also an array (inner arrays).
#The inner arrays have 3 elements of their own: [message length, message number, message contents]
class MaxHeapMessages:
    #creates array based on input array
    #input array is a list of lists: [[message length, message number, message contents], ...
    #each element of this list is: [message length, message number, message contents]
    def __init__(self, input_array):
        self.array = input_array

    def heapify(self):
        start = (len(self.array) -2)/2
        while start >= 0:
            self.siftDown(self.array,start,len(self.array)-1)
            start -= 1

    def siftDown(self, A, start, end):
        root = start
        while root * 2 + 1 <= end:
            child = root * 2 + 1
            if child +1 <= end and A[child][0] > A[child + 1][0]:
                child += 1
            if child <= end and A[root][0] > A[child][0]:
                A[root], A[child] = A[child],A[root]
                root = child
            else:
                return
            
    def heapSort(self):
        self.heapify()
        end = len(self.array) - 1
        while end > 0:
            self.array[end],self.array[0] = self.array[0], self.array[end]
            self.siftDown(self.array, 0, end - 1)
            end -= 1
        return

    def push_message(self, element):
        self.array.append(element)
        self.heapSort()
        
    def pop_message(self, element = 0):
        output = self.array.pop(element)
        self.heapSort()
        return output

    #Returns the position of the element that is less than or equal to the variable: Val
    def searchLessThan_Position(self, val):
        unsorted_array = []
        position = 0
        for position,element in enumerate(self.array): #enumerate(self.array[0:-1])
            if element[0] <= val:
                unsorted_array.append([position,element])
        if len(unsorted_array) > 1:
            sorted_array = self.bubbleSortDescending(unsorted_array)
            return sorted_array[0][0]
        if len(unsorted_array) == 0: #Item was NOT found!
            return -1
        #Single item was found    
        return unsorted_array[0][0]

    #Returns the value of the element that is less than or equal to the variable: Val
    def searchLessThan_Value(self,val):                    
        unsorted_array = []
        position = 0
        for position,element in enumerate(self.array[1:-1]):
            if element[0] <= val:
                unsorted_array.append([position,element])
        if len(unsorted_array) > 1:
            sorted_array = self.bubbleSortDescending(unsorted_array)
            return sorted_array[0][1]
        if len(unsorted_array) == 0:
            return -1
        return unsorted_Array[0][1]
        
    def searchLessThan_Pop(self, val):
        position = self.searchLessThan_Position(val)
        if position != -1:
            return self.pop(position)
        else:
            return -1
        
    #A special BubbleSort that takes a unique array input
    #Array input structure: [[position0, element0],[position1,element1], ...]
    #Element structure: element0 = [message length, message number, message contents]
    def bubbleSortDescending(self, input_array):
        for passNum in range(len(input_array)-1,0,-1):
            for i in range(passNum):
                if input_array[i][1][0] < input_array[i+1][1][0]:
                    temp = input_array[i]
                    input_array[i] = input_array[i+1]
                    input_array[i+1] = temp
        return input_array

    def bubbleSortAscending(self, input_array):
        for passNum in range(len(input_array)-1,0,-1):
            for i in range(passNum):
                if input_array[i][1][0] > input_array[i+1][1][0]:
                    temp = input_array[i]
                    input_array[i] = input_array[i+1]
                    input_array[i+1] = temp
        return input_array
        
    def getMessageLength(self, element):
        return self.array[element][0]

    def getMessageNumber(self, element):
        return self.array[element][1]

    def getMessageContents(self, element):
        return self.array[element][2]
    
    def printArray(self):
        count = 0
        for i in self.array:
            print "Node:", count
            print "Message Length: ",i[0]
            print "Message Number: ", i[1]
            print "Message Contents: ", i[2]
            count += 1
        return

class Reorganize:

    def __init__(self, directory):
        global ref_val

        ### Input Directory
        self.directory = directory
        
        self.input_file_list = []
        self.input_file_paths = []

        self.output_directory = []
        self.output_directory_MSG_temp = []
        self.output_directory_MSG = []
        
        self.output_file_list = []
        self.output_file_paths = []

        self.output_file_path_temp = []

        #Help parse messages that go over 1 line
        self.static_message_length = 0
        self.static_message_number = ""
        self.static_message_contents = ""
        self.static_continue_message = 0
        self.multi_line_spacer = "^^^"

        #Array of messages from single file to turn into a Heap
        self.messages_heap_array = []
        self.current_space = ref_val  #Keep track of current_space in 2D bin-packing array

        #Used to Calculate Percent Compression and Percent Wasted
        self.before_count = 0  #Before MaxHeap and 2D bin packing Algorithm
        self.before_unused = 0 #Before MaxHeap and 2D bin packing Algorithm
        self.before_rows = 0 #Before MaxHeap and 2D bin packing Algorithm
        
        self.after_count = 0 #After MaxHeap and 2D bin packing Algorithm
        self.after_unused = 0 #After MaxHeap and 2D bin packing Algorithm
        self.after_rows = 0 #After MaxHeap and 2D bin packing Algorithm

        #Independent MSG File Order - Used to Calculate Percent Compression
        #Array Structure for Before and After Arrays: [ [MSG File Name, # of unused characters], ... ]
        #Array Structure for Ideal Msg Array: [ [MSG File Name, # of characters for messages in that file] , ... ]
        self.ideal_msg_array = []
        self.unused_before_array = []
        self.unused_after_array = []
        
        #Ideal Reference Point to Calculate Percent Compression and Percent Wasted
        self.ideal_used = 0

        #Keeping track of MSG files being processed
        self.last_file = 0 #Keep track of how many files to be processed
        self.current_file_num = 0 #Keep track of current file
        self.current_file_name = ""
        self.previous_file_num = -1 #Keep track of previous file
        self.previous_file_name = ""

    def verifyDirectory(self):
        self.directory = self.directory.replace("\\\\", '//')
        self.directory = self.directory.replace("\\", '/')
        return

    def setDirectoryName(self, folder = None):
        if folder is None:
            return False
        else:
            self.directory = folder
            return True

    #Get Static Fields
    def getMessageLength(self):
        return self.static_message_length
    def getMessageNumber(self):
        return self.static_message_number
    def getMessageContents(self):
        return self.static_message_contents
    def getContinueMessage(self):
        return self.static_continue_message

    #Set Static Fields
    def setMessageLength(self, length):
        self.static_message_length = length
        return
    def setMessageNumber(self, number):
        self.static_message_number = number
        return
    def setMessageContents(self, string):
        self.static_message_contents = string
    def setContinueMessage(self, number):
        self.static_continue_message = number
        return
    
    def setMessagesHeapArray(self, array):
        self.messages_heap_array = array
        return
        
    def createFolder(self,directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            return True
        except:
            print "Error: Creating directory: ",directory
            return False

    def generateFileList(self, output = None):
        global generate_input_file_list
        
        allFilesArray = []
        for dirpath, dirnames, files in os.walk(self.directory):  #yields a 3-tuple (dirpath, dirnames, filenames).
            for name in files:
                allFilesArray.append([dirpath, name, os.path.join(dirpath,name)])
        filesDF = pd.DataFrame(allFilesArray, columns = ["Path","File","FullPath"])

        if ((output != None) and (generate_input_file_list == True)):
            filesDF.to_csv(self.output_directory + "/Input_File_List.csv", index = True, header = True)

        self.input_file_list = filesDF["File"]
        self.input_file_paths = filesDF["FullPath"]

    def setOutputDirectory(self, path_exists, output_directory):
        if path_exists == True:
            self.output_directory = output_directory
            self.output_directory_MSG_temp = output_directory + "/MSG/TEMP/"
            self.output_directory_MSG = output_directory + "/MSG/"

    def copyFiles(self, output = None):
        global generate_output_file_list

        outputFileArray = []
        temp_folder = self.output_directory_MSG_temp #os.getcwd() +
        
        ###################################################
        ### Delete all existing files in TEMP directory   #
        ###################################################
        
        for eachFile in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, eachFile)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                #If you want to remove all sub-directories, add this line (uncomment it): elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

        ################################################################
        ### Copy all MSG files in Input_Directory to TEMP directory    #
        ################################################################

        for filePath in self.input_file_paths:
            shutil.copy(filePath,  self.output_directory_MSG_temp) #os.getcwd() +
        for dirpath, dirnames, files in os.walk(self.output_directory_MSG_temp):
            for name in files:
                outputFileArray.append([dirpath, name, os.path.join(dirpath,name)])
        filesDF = pd.DataFrame(outputFileArray, columns =["Path", "File", "FullPath"])

        #Generate output file fields
        self.output_file_list = filesDF["File"]  #list of all the output MSG files
        self.output_file_path_temp = filesDF["FullPath"]

        #Create Initial MSG Output Files
        for output_file in self.output_file_list:
            output_file_path = self.output_directory_MSG + output_file
            self.output_file_paths.append(output_file_path)
            if(automatic_MSG_output == True):
                with open(output_file_path, 'w+') as f:
                    f.close()

        if (output != None and (generate_output_file_list == True)):
            filesDF.to_csv(self.output_directory + output_file_list, index = True, header = True)

    def printFields(self):
        print "Input Directory: \n{}" .format(self.directory)

        print "\nInput File List:"
        for i in self.input_file_list:
            print i
            
        print "\nInput File Path:"
        for i in self.input_file_paths:
            print i
            
        print "\nOutput File List:"
        for i in self.output_file_list:
            print i
    
        print "\nOutput File Path:"
        for i in self.output_file_paths:
            print i

        print "\nOutput Directory: \n{}" .format(self.output_directory)
        
        print "\nTEMP MSG Directory:"
        for i in self.output_file_path_temp:
            print i

    def copyLine(self, input_string, output_file):
        if(automatic_MSG_output == True):
            with open(output_file, "a") as f:
                f.write(input_string)
                f.close()
        return
    
    def copyMessageLine(self, input_string, output_file):
        with open(output_file, "a") as f:
            f.write(input_string)
            f.close()
        return
            
    #Function Calls: self.copyLine(), algorithmWrite(), classifyMessage()
    def locateMSGFiles(self):
        global file_independent
        global message_block_separator
        global MSG_file_order
        global config_file_name
            
        #Open Message File to be written to later
        if(write_message_file == True):
            f = open(message_file, "w")
            f.write(message_file_header)
            f.close()
        
        #Determines the array number of the last file (should be 19, since counting arrays from 0)
        #Only used in depreciated function (after_compression())
        #self.last_file = len(self.output_file_path_temp) -1

        #Use specified file order in "MSG_file_order" array
        if(file_independent == 0):
            abs_file_num = 0
            #Processes Messages in the order they are uploaded to SCADA and thereby stored in SCADA Message Memory Buffer
            for MSG_file in MSG_file_order: #Iterate through each MSG file in the order it is uploaded to SCADA
                for file_num, file_path in enumerate(self.output_file_path_temp): #get list of MSG files from local folder copied from network drive (ASPEN)
                    file_name = file_path.split("/")[-1]
                    if(MSG_file.upper() == file_name.split("_")[0].upper()): #Determine when match is found between MSG Order in SCADA and Local MSG files
                        self.locateMessages(abs_file_num, file_path)
                        abs_file_num += 1
                        break
                    
        #MSG File independent order
        elif(file_independent == 1):
            for file_num, file_path in enumerate(self.output_file_path_temp): #get list of MSG files from local folder copied from network drive (ASPEN)
                print "File Num: {}".format(file_num)
                print "File Path: {}" .format(file_path)
                self.locateMessages(file_num, file_path)    

        return #End of locateMSGFiles() Function
    
    def locateMessages(self, file_num, file_path):
        global message_independent
        #Get Current File Name of MSG File being processed
        ### Previous had a for loop... for file_num, file_path in enumerate(self.output_file_path_temp):
        self.current_file_num = file_num  #Store current MSG file number
        self.current_file_name = file_path.split("/")[-1] #Store current MSG file name

        #Check if new MSG file is being processed, update before and ideal arrays, reset variables
        if(self.previous_file_num != self.current_file_num):
            self.previous_file_num = self.current_file_num #Update previous_file_num 
            self.unused_before_array.append([self.current_file_name, 0]) #Add next MSG file unused_space
            self.unused_after_array.append([self.current_file_name, 0]) #Add next MSG file unused_space
            self.ideal_msg_array.append([self.current_file_name, 0]) #Add next MSG file ideal msg space
        if(message_independent == 1):
            self.before_unused = 0 #Reset Before Unused
            self.before_count = 0 #Reset Before Count
            self.after_unused = 0 #Reset After Unused
            self.after_count = 0 #Reset After Count
            self.ideal_used = 0 #Reset Ideal Used

        #Write Output Message File
        if(write_message_file == True):
            file_name = file_path.split("/")[-1]
            self.copyMessageLine("\n" + new_file_header + "\n", message_file)
            self.copyMessageLine("\n" + file_name + "\n", message_file)

        #Set Variables
        messages_flag = 0
        heapify_array = []
        output_file_path = self.output_file_paths[file_num]
        open_input_file = open(file_path, 'r')

        #Print to console current file being processed
        print "Current File: ", file_path
        
        for line_num, line in enumerate(open_input_file):
            #Capture all commented out lines before messages
            if(messages_flag == 0 and ("#" in line)):
                self.copyLine(line, output_file_path)
                continue
            #Capture all non-message lines
            elif((messages_flag == 0) and not("AM!" in line[0:3])):
                self.copyLine(line, output_file_path)
                continue
            #Capture Start of Messages Block
            elif(messages_flag == 0) and ("AM!" in line[0:3]):  #activates messages_flag when the messages indicator is reached
                self.copyLine(line, output_file_path)
                messages_flag = 1
                continue
            #Capture End of Messages Block
            elif((messages_flag ==1) and ("$" in line)):

                #Create separator blocks for Message Order File
                if(write_message_file == True):
                    self.copyLine("\n" + message_block_separator + "\n", message_file)
                
                messages_flag = 0 #Reset messages flag
                line = self.classifyMessage(line, output_file_path)
                if (line != None):
                    heapify_array.append(line)

                #*** Calculate Pre-Optimized Compression ***
                self.before_compression(heapify_array)

                #*** Output Messages to file using MaxHeap Algorithm ***
                if(message_independent == 1):
                    self.algorithmWrite_Ind(heapify_array, output_file_path)

                elif(message_independent == 0):
                    self.algorithmWrite(heapify_array, output_file_path)
    
                heapify_array = [] #Reset heapify array
                continue
            #Capture Commented Out Messages
            elif((messages_flag == 1) and ("#" in line)):
                self.copyLine(line, output_file_path)
                continue
            #Capture Messages, store in MaxHeap
            elif((messages_flag == 1) and not("#" in line)):
                line = self.classifyMessage(line, output_file_path)
                if (line != None):
                    heapify_array.append(line)
                continue

        #End of Inner For Loop

        #Check if Messages are at the end of the File
        if (messages_flag == 1):
            
            #*** Calculate Pre-Optimized Compression ***
            self.before_compression(heapify_array)
            
            if(message_independent == 1):
                self.algorithmWrite_Ind(heapify_array, output_file_path)

            elif(message_independent == 0):
                self.algorithmWrite(heapify_array, output_file_path)
       
            #Reset Variables
            messages_flag = 0
            heapify_array = []
            
        #End of Outer For Loop        
        return

    #Deprecated (not used)
    #Determines how to pop elements off of the MaxHeap to satisfy the 336 row length, and optimize message compression
    #Calls: writeMessageToFile() to 
    def algorithmWrite_Original(self, input_array, output_file_path):
        global ref_val
        messageHeap = MaxHeapMessages(input_array)
        messageHeap.heapify()
        messageHeap.heapSort()
        
        while(len(messageHeap.array) > 2):
            next_line_flag = 0
            #Take Max Value, find difference
            max_val = messageHeap.array[0][0]
            difference = ref_val - max_val

            first_message = messageHeap.pop_message() #Pop max value

            #Calculate Post-Optimized Compression
            self.after_compression(first_message)
            
            self.writeMessageToFile(first_message, output_file_path) #Function to write message to file

            #Write messages to MSG file that fit in the remaining space
            while (next_line_flag == 0 and (len(messageHeap.array) > 2)):   
                #for value in range(difference, 0, -1):
                    array_position = messageHeap.searchLessThan_Position(difference)
                    if (array_position != -1): #Found a message that is small enough to fit in the remaining space!
                       #Write message to file 
                        output_message = messageHeap.pop_message(array_position)    #Output message
                        output_message_length = output_message[0]                   #Output message length
                        difference = difference - output_message_length             #Remaining length in the line

                        #Calculate Post-Optimized Compression
                        self.after_compression(output_message)
                        
                        self.writeMessageToFile(output_message, output_file_path)   #Write Output Message to MSG File
                        break
                    else: #Unable to find any messages that are small enough to fit in the remaining space!
                        next_line_flag = 1
                        break
                #break    
        #End of While Loop
                    
        if (len(messageHeap.array) == 2):
            output_message = messageHeap.pop_message()
            self.writeMessageToFile(output_message, output_file_path)
            output_message = messageHeap.pop_message()

            #Calculate Post-Optimized Compression
            self.after_compression(output_message, 1)
           
            self.writeMessageToFile(output_message, output_file_path, 1)

        elif(len(messageHeap.array) == 1):
            output_message = messageHeap.pop_message()

            #Calculate Post-Optimized Compression
            self.after_compression(output_message, 1)
           
            self.writeMessageToFile(output_message, output_file_path, 1)
              
        return  #End of algorithmWrite() Function 

    #Need to consider the last MSG file, to prevent additional counting!!!
    def algorithmWrite(self, input_array, output_file_path):
        global ref_val
        messageHeap = MaxHeapMessages(input_array)
        messageHeap.heapify()
        messageHeap.heapSort()
        
        space_array = [[self.current_space,[]]] #Optimize organization of Alarm Messages
        
        while(len(messageHeap.array) > 0):
            new_line_flag = 1 #Reset New Line Flag
            current_message = messageHeap.pop_message() #Pop and heapSort 

            for element in space_array:
                if(element[0] - current_message[0] >= 0):
                    element[1].append(current_message)
                    element[0] -= current_message[0]
                    new_line_flag = 0
                    break
            if(new_line_flag != 0):
                space_array.append([ref_val - current_message[0],[current_message]])
                self.after_rows += 1
        #End of While Loop
        self.after_rows -= 1
        
        #Set self.current_space to the remaining space of the last element in space_array
        self.current_space = space_array[-1][0]
           
        for num,element in enumerate(space_array):
            count_flag = 0
            for msg_num, message in enumerate(element[1]):
                if(num == len(space_array)-1) and (msg_num == len(element[1])-1): #Find the last message in the Message Block
                    self.writeMessageToFile(message, output_file_path, 1) #Write message to file with end of messages character, "$"
                else:
                    self.writeMessageToFile(message, output_file_path)

                    #Calculate Unused space, conditional statement prevents counting the last row!
                if(count_flag != 1 and (num != len(space_array)-1) and (msg_num != len(element[1])-1)):
                    count_flag = 1 
                    self.after_unused += element[0]
                       
            #End of Inner For Loop
        #End of Outer For Loop     
        return  #End of algorithmWrite() Function
                       
    def algorithmWrite_Ind(self, input_array, output_file_path):
        global ref_val
        messageHeap = MaxHeapMessages(input_array)
        messageHeap.heapify()
        messageHeap.heapSort()

        #space_array format --> each element is a line in the message block
        #Each element is composed of two inner elements. 1st inner element --> current remaining space to make decision of where to put the next message
        #2nd inner element --> array that contains messages that are stored on that line
        #space_array = [ [unused space in line, [message1, message2, message 3, ...] ], [unused space in line, [message1, message2, message 3, ...], ...]
        #Each message, example message1 --> [length of message1, message1's number (e.g. EX134 is 134), message1's contents]

        space_array = [ [self.current_space,[] ] ] #Optimize organization of Alarm Messages
        
        while(len(messageHeap.array) > 0):
            new_line_flag = 1 #Reset New Line Flag
            current_message = messageHeap.pop_message() #Pop and heapSort 

            for element in space_array:
                if(element[0] - current_message[0] >= 0):
                    element[1].append(current_message)
                    element[0] -= current_message[0]
                    new_line_flag = 0
                    break
            if(new_line_flag != 0):
                space_array.append([ref_val - current_message[0],[current_message]])
                self.after_rows += 1
        #End of While Loop
        self.after_rows -= 1
        
            #Set self.current_space to the remaining space of the last element in space_array
            #self.current_space = space_array[-1][0]
        #Reset the self.current_space variable, as we are considering the files INDEPENDENTLY from one another
        self.current_space = ref_val
        
        for num,element in enumerate(space_array):
            count_flag = 0
            for msg_num, message in enumerate(element[1]):
                if(num == len(space_array)-1) and (msg_num == len(element[1])-1): #Find the last message in the Message Block
                    self.writeMessageToFile(message, output_file_path, 1) #Write message to file with end of messages character, "$"
                else:
                    self.writeMessageToFile(message, output_file_path)
            
            #Calculate Unused space - After Optimization Algorithm
                if(count_flag != 1 and (num != len(space_array)-1) and (msg_num != len(element[1])-1)):
                    count_flag = 1
                    self.unused_after_array[self.previous_file_num][1] += element[0]
        
            #End of Inner For Loop
        #End of Outer For Loop
        return  #End of algorithmWrite_Ind() Function
                       
    def classifyMessage(self, line, output_file_path):
        #self.static_message_length = 0
        #self.static_message_number = ""
        #self.static_message_contents = ""
        #self.static_continue_message = 0

        message_length = 0
        message_number = ""
        message_contents = ""
        output_array = []
        
        #Flag for when inside the message
        inner_message_flag = 0

        try:
            #Case 0 - Commented out line. Directly copied to output file.
            if (line[0] == "#"):
                self.copyLine(line, output_file_path)
                return None

            #Case 1 - Message only spans a single line
            elif (self.static_continue_message == 0 and (ord(line[0]) >=48 and ord(line[0]) <=57) and (("!" in line[-4:-1]) or ("$" in line[-4:-1])) ):
                inner_message_flag = 0
                for char_num, char in enumerate(line):
                    if(inner_message_flag == 0 and (ord(char) >=48 and ord(char) <=57)):
                        message_number = message_number + str(char)
                        continue
                    elif(inner_message_flag == 0 and not(ord(char) >=48 and ord(char) <=57)):
                        inner_message_flag = 1
                        continue
                    elif(inner_message_flag == 1 and (char == "'")):
                        inner_message_flag = 2
                        continue
                    elif(inner_message_flag == 2 and not(char == "'")):
                        message_contents = message_contents + str(char)
                        continue
                    elif(inner_message_flag == 2 and char == "'"):
                        inner_message_flag = 3 #Does not match any condition, End of the line

                #Output the Message into an Array 
                message_length = len(message_contents)
                output_array = [message_length, int(message_number), message_contents]

                return output_array
                 
            #Case 2 - Message starts on this line, but continues to the next line
            elif ((self.static_continue_message == 0) and ("&" in line[-4:-1])):
                inner_message_flag = 0
                self.static_continue_message = 1
                for char_num, char in enumerate(line):
                    if(inner_message_flag == 0 and (ord(char) >=48 and ord(char) <= 57)):
                       self.static_message_number = self.static_message_number + str(char)
                       continue
                    elif(inner_message_flag == 0 and not(ord(char) >=48 and ord(char) <= 57)):
                        inner_message_flag = 1
                        continue
                    elif(inner_message_flag == 1 and (char == "'")):
                        inner_message_flag = 2
                        continue
                    elif(inner_message_flag == 2 and not(char == "'")):
                        self.static_message_contents = self.static_message_contents + str(char)
                        continue
                    elif (inner_message_flag == 2 and char == "'"):
                        inner_message_flag = 3 #Does not match any condition, End of the line

                #Put in unique spacer of "^^^" to later splice the multi-line messages
                self.static_message_contents = self.static_message_contents + self.multi_line_spacer
                return None        
                    
            #Case 3 - Message is continued from previous line, and continues to the next line (end of line character is &)
            elif ((self.static_continue_message != 0) and ("&" in line[-4:-1])):
                inner_message_flag = 0
                self.static_continue_message = 2
                for char_num, char in enumerate(line):
                    if(inner_message_flag == 0 and (char == "'")):
                        inner_message_flag = 1
                        continue
                    elif(inner_message_flag == 1 and not(char == "'")):
                        self.setMessageContents(self.getMessageContents() + str(char))
                        continue
                    elif(inner_message_flag == 1 and (char == "'")):
                        inner_message_flag = 2

                #Put in unique spacer of "^^^" to later splice the multi-line messages
                self.static_message_contents = self.static_message_contents + self.multi_line_spacer
                return None
                
            #Case 4 - Message is continued from the previous line, but terminates on this line
            elif((self.static_continue_message != 0) and ("!" in line[-4:-1])):
                inner_message_flag = 0
                for char_num, char in enumerate(line):
                    if(inner_message_flag == 0 and (char == "'")):
                        inner_message_flag = 1
                        continue
                    elif(inner_message_flag == 1 and not(char == "'")):
                        self.setMessageContents(self.getMessageContents() + str(char))
                        continue
                    elif(inner_message_flag == 1 and (char == "'")):
                        inner_message_flag = 2
                        continue
                    
                #Output the Message into an Array 
                message_length = len(self.static_message_contents) - 3*(self.static_continue_message)
                output_array = [message_length, int(self.static_message_number), self.static_message_contents]   

                #Reset Variables
                inner_message_flag = 0
                self.static_message_length = 0
                self.static_message_number = ""
                self.static_message_contents = ""
                self.static_continue_message = 0

                return output_array #Returns the multi-line message (recall: with "^^^" as spacer characters between each line)

            #Case 5 - Message is continued from the previous line, terminates on this line, and is the end of the messages
            elif((self.static_continue_message != 0) and ("$" in line)):
                inner_message_flag = 0
                for char_num, char in enumerate(line):
                    if(inner_message_flag == 0 and (char == "'")):
                        inner_message_flag = 1
                        continue
                    elif(inner_message_flag == 1 and not(char == "'")):
                        self.static_message_contents = self.static_message_contents + str(char)
                        continue
                    elif(inner_message_flag == 1 and (char == "'")):
                        inner_message_flag = 2
                        continue

                #Flag to indicate it is the End of the Messages Section
                self.static_message_contents = self.static_message_contents + "%%%"

                #Output the Message into an Array 
                message_length = len(self.static_message_contents) - 3*(self.static_continue_message)
                output_array = [message_length, int(self.static_message_number), self.static_message_contents]   

                #Reset Variables
                inner_message_flag = 0
                self.static_message_length = 0
                self.static_message_number = ""
                self.static_message_contents = ""
                self.static_continue_message = 0

                return output_array #Returns the multi-line message with "^^^" as spacer characters between each line

            #Case 6 - The message is a single line, but also the last message of the MSG File
            elif(self.static_continue_message == 0 and ("$" in line)):
                inner_message_flag = 0
                for char_num, char in enumerate(line):
                    if((char_num == 0) and (char == "#")):
                        self.copyLine(line, output_file_path)
                        return
                    elif (inner_message_flag == 0 and (ord(char) >= 48 and ord(char) <= 57)):
                        message_number = message_number + str(char)
                        continue
                    elif(inner_message_flag == 0 and not(ord(char) >= 48 and ord(char) <= 57)):
                         inner_message_flag = 1
                         continue
                    elif(inner_message_flag == 1 and (char == "'")):
                         inner_message_flag = 2
                         continue
                    elif(inner_message_flag == 2 and not(char == "'")):
                        message_contents = message_contents + str(char)
                        continue
                    elif(inner_message_flag == 2 and (char == "'")):
                         inner_message_flag = 3
                         continue

                #Flag to indicate it is the End of the Messages Section
                message_contents = message_contents + "%%%"
                
                #Reset Parameters
                inner_message_flag = 0

                #Output the Message into an Array 
                message_length = len(message_contents)
                output_array = [message_length, int(message_number), message_contents]

                return output_array
            
        except:
            #This result should NEVER be run!! The MSG code is otherwise written incorrectly!
            print "Error: Unable to properly parse messages in MSG file: ", output_file_path
            print "Message: ", line
            print "Status variables: Continue Message: ", self.static_continue_message
            return None

    #Writes messages to:
    #1) Message Order File: Provides suggested order to place messages to optimized positions in each Message Block
    #2) MSG Blueprint Files: Provides 20 MSG files with messages reorganized into optimal positions 
    def writeMessageToFile(self, message, output_file_path, last_line = 0):
        global write_message_file
        
        message_length = message[0]
        message_number = str(message[1])
        message_contents = message[2]
        output_string = ""
        
        #Check if Message is at the end of the Messages (needs "$" character at the end of the Message Contents)
        split_contents = message_contents.split("%%%")
        end_of_messages_flag = len(split_contents)
                                
        if(end_of_messages_flag == 2):
            message_contents = split_contents[0]        
              
        message_contents = message_contents.split("^^^")
        number_of_lines = len(message_contents)

        #Message Number
        output_string = output_string + message_number + "!"

        #*** Writes Order of Messages to Message Order File ***
        if (write_message_file == True):
            self.copyMessageLine(message_number + "\n", message_file)

        for line in range(0,number_of_lines):
            if(line == (number_of_lines -1) and (last_line == 0)):
                output_string = output_string + "'" + message_contents[line] + "'" + "!" + "\n"
                break
            elif(line == (number_of_lines -1) and (last_line != 0)):
                output_string = output_string + "'" + message_contents[line] + "'" + "$" + "\n"
                break
            output_string = output_string + "'" + message_contents[line] + "'" + "!" + "\n"
        
        #Write Message to File
        self.copyLine(output_string, output_file_path)
                
        return #End of writeMessageToFile
    def before_compression(self, input_array):
        global message_independent
        global file_independent
        global ref_val
        reset_flag = 0
        
        if(message_independent == 1 or file_independent == 1):
            #Calculate the number of Unused Message Space    
            for num, message in enumerate(input_array):
                self.ideal_used += message[0]
                if((self.before_count + message[0]) > ref_val):
                    self.before_rows += 1
                    #Ignore the additional characters that are produced at the end of the message block
                    #(approximation due to individualizing the MSG file alarm messages)
                    if(num != len(input_array)-1): 
                        self.before_unused += (ref_val - self.before_count)
                    self.before_count = message[0]
                else:
                    self.before_count += message[0]        
            
            self.unused_before_array[self.previous_file_num][1] += self.before_unused #Store unused_before space
            self.ideal_msg_array[self.previous_file_num][1] += self.ideal_used #Store ideal message space       
                
        elif(message_independent == 0 or file_independent == 0):
            for num, message in enumerate(input_array):
                #Calculate Reference Point (perfect compression, no waste) to determine Message Optimization effiency
                self.ideal_used += message[0]
                if((self.before_count + message[0]) > ref_val):
                    self.before_rows += 1
                    self.before_unused += (ref_val - self.before_count) #Find Unused space on a given line
                    self.before_count = message[0] #Reset Count Variable
                else:
                    self.before_count += message[0]
            #Prevent over-counting of new rows, Remove extra row at the end of the message block, it is incorporated as the starting point of the next message block
            self.before_rows -= 1
        return

    #Depreciated - Error, Unable to compute: self.unused_after_array[self.previous_file_num][1] += unused_space
    #Computed internally within Function: algorithmWrite_Ind()
    def after_compression(self, unused_char_space, last_message = 0):
        global message_independent               
        global ref_val

        if(message_independent == 1):
        
            previous_value = self.unused_after_array[self.previous_file_num][1]
            updated_value = previous_value + unused_char_space
            self.unused_after_array[self.previous_file_num][1] = updated_value
            #self.unused_after_array[self.previous_file_num][1] += unused_space #Store unused_before space
        return

    #Depreciated - No longer used
    def after_compression_Dep(self, message, last_message = 0):
        global message_independent               
        global ref_val

        if(message_independent == 1):
            if (self.previous_file_num != self.current_file_num):
                self.previous_file_num = self.current_file_num #Update Previous_file_num
                self.unused_after_array.append([self.current_file_name,]) #Add next MSG file unused_space
                
                self.after_unused += (ref_val - self.after_count) #End of previous file, store the remaining unused space
                self.unused_after_array[self.previous_file_num][1] = self.after_unused #Store unused_before space

                self.after_unused = 0 #Reset After Unused
                self.after_count = 0 #Reset After Count
                
                self.previous_file_num = self.current_file_num #Update the previous_file_num to the current_file_num
                
            elif(self.previous_file_num == self.current_file_num):
                if((self.after_count + message[0]) > ref_val):
                    self.after_rows += 1
                    self.after_unused += ref_val - self.after_count #Find Unused space on a given line
                    self.after_count = 0 #Reset Count Variable
                else:
                    self.after_count += message[0]
                       
        elif(message_independent == 0):               
            if((self.after_count + message[0]) > ref_val):
               self.after_rows += 1
               self.after_unused += ref_val - self.after_count #Find Unused space on a given line
               self.after_count = 0 #Reset Count Variable
            else:
               self.after_count += message[0]

            #if(self.current_file_num == self.last_file) and (last_message != 0):
            #   self.after_unused += ref_val - self.after_count
        return

    
    def choose_calc_optimization(self):
        global message_independent
                       
        if(message_independent == 0):
            self.calculate_optimization()

        elif(message_independent == 1):
            self.calculate_optimization_Ind()
        return
                       
    def calculate_optimization(self):
        global ref_val
        global row_limit
        global message_file
        global new_file_header
        
        total_characters = ref_val * row_limit
                
        #Calculating Efficiency Before applying Optimization Algorithm
        before_char_used = self.ideal_used + self.before_unused
        
        #Old way of calculating efficiency
        #before_efficiency = self.ideal_used/float(before_char_used)
        
        before_efficiency = float(self.before_unused + self.ideal_used)*100/self.ideal_used
        before_compression = (1 - (float(self.before_unused)/total_characters))
        before_waste =  float(self.before_unused)/total_characters
        #before_lines = self.before_rows

        #Calculating Efficiency After applying Optimization Algorithm
        after_char_used = self.ideal_used + self.after_unused
        
        #Old way of calculating efficiency
        #after_efficiency = self.ideal_used/float(after_char_used)

        after_efficiency = float(self.after_unused + self.ideal_used)*100/self.ideal_used
        after_compression = (1 - (float(self.after_unused)/total_characters))
        after_waste = float(self.after_unused)/total_characters
        #after_lines = self.after_rows

        percent_improvement = '%.2f'%( 100 * (after_efficiency - before_efficiency) / float(before_efficiency) ) + "%"

        print "\n*** Results of Alarm Message Optimization Algorithm ***\n"
        
        print "Before Compression: ", before_compression
        print "Before Waste: ", before_waste
        print "Before Efficiency: ", before_efficiency
        #print "Before Lines Used: ", before_lines

        print "After Compression: ", after_compression
        print "After Waste: ", after_waste
        print "After Efficiency: ", after_efficiency
        #print "After Lines Used: ", after_lines

        print "Percent Improvement: {}" .format(percent_improvement)

        #Open Message Order File, and write Percent Optimization Improvement:
        input_text = "\nPERCENT IMPROVEMENT (due to Optimization): " + percent_improvement + "\n\n Improvement is a comparison of 'Current' vs 'Optimized' Alarm Message Organization."
        self.writeLineToFile(input_text, new_file_header, message_file)

        #Plotting Graphs
        self.plotting(before_efficiency, after_efficiency)
        
        return

    def calculate_optimization_Ind(self):
        global ref_val
        global row_limit
        global message_file
        global new_file_header

        output_calc = []
        net_ideal = 0
        net_before = 0
        net_after = 0
        
        for file_num, file_ele in enumerate(self.ideal_msg_array):
            ideal_msg = self.ideal_msg_array[file_num][1]
            unused_before = self.unused_before_array[file_num][1]
            unused_after = self.unused_after_array[file_num][1]
            net_ideal += ideal_msg
            net_before += unused_before
            net_after += unused_after

            if (ideal_msg == 0):
                unused_before = 0
                unused_after = 0
            else:
                unused_before = 100*float(unused_before + ideal_msg)/float(ideal_msg)
                unused_after = 100*float(unused_after + ideal_msg)/float(ideal_msg)
                ideal_msg = (ideal_msg/ideal_msg)*100
           
            output_calc.append([file_ele[0], ideal_msg, unused_before, unused_after])

        #Variables used for plotting function - self.plotting_Inp()
        net_before = float((net_before + net_ideal)*100)/net_ideal
        net_after = float((net_after + net_ideal)*100)/net_ideal

        print "\n*** Results of Alarm Message Optimization Algorithm ***\n"
        #for element in output_calc:
        #    print "Output File: {}", element[0], " Ideal: ", element[1], "%  ,Before: ", element[2], "%  ,After: ", element[3], "%"

        print "\nBefore Optimization: ", net_before, "% \nAfter Optimization: ", net_after, "%"

        #Open Message Order File, and write Percent Optimization Improvement:
        percent_improvement = '%.2f' %abs(( 100 * (net_before - net_after) / float(net_before) ) ) + "%"
        improvement = '%.2f' %(net_before - net_after) + "%"
        
        print "\nPERCENT IMPROVEMENT: {}" .format(percent_improvement)
        print "\nIMPROVEMENT: {}" .format(improvement)
        #input_text = "\nPERCENT IMPROVEMENT (due to Optimization): " + percent_improvement + "\nNote: Improvement is a comparison of 'Current' vs 'Optimized' Alarm Message Organization."
        input_text = "\nIMPROVEMENT (due to Optimization): " + improvement + "\nNote: Improvement is a comparison of 'Current' vs 'Optimized' Alarm Message Organization."
        self.writeLineToFile(input_text, new_file_header, message_file)

        #####################################
        ### Plot the Results                #
        #####################################
        self.plotting_Inp(output_calc, net_before, net_after)
        return

    def writeLineToFile(self, input_line, identifier_line, output_file):
        #Read contents of file into Memory
        with open (output_file, 'r') as f:
            text = f.readlines()

        #Find location in the file to change (first occurance of trigger "identifier_line")
        text_location = None
        for num, line in enumerate(text):
            if(identifier_line in line):
                text_location = num
                break

        #Change specific line in the file with new addition
        if text_location is not None:
            text[text_location] = input_line + "\n\n" + text[text_location]

        #Write Back to the File
        with open(output_file, "w") as f:
            f.writelines(text)
        return

    def plotting_Inp(self,output_array, net_before, net_after):
        global automatic_graph_output
        global python_output_directory
        
        textstr = '%.2f' %(net_before - net_after) + "%"
        textstr = "Total Improvement: " + textstr 

        numbers = []
        ideal_numbers = []
        before_numbers = []
        after_numbers = []
        name_array = []
        before_array = []
        after_array = []
        ideal_array = []

        net_name= "Total"
        
        #Output_array Structure: [file_ele[0], ideal_msg, unused_before, unused_after]
        output_array.append(["TOTAL IMPROVEMENT", 100, net_before, net_after])

        #Separate MSG File Names, Before Optimization, After Optimization, and
        #Ideal (always 100%) into separate arrays to be plotted

        num = 0
        for element in output_array:
            numbers.append(num)
            before_numbers.append(num - 0.5)
            after_numbers.append(num)
            ideal_numbers.append(num + 0.5)
            name_array.append(element[0].split(".txt")[0])
            ideal_array.append(element[1])
            before_array.append(element[2])
            after_array.append(element[3])
            num += 2
        
        fig = plt.figure(1, figsize = (20,10))
        
        top_offset = 0.07
        left_offset = 0.15
        right_offset = 0.2
        bottom_offset = 0.13
        hgap = 0.1
        ax_width = 1 - left_offset - right_offset
        ax_height = (1 - top_offset - bottom_offset - hgap)/float(2)
        #ax1 = fig.add_axes([left_offset, bottom_offset + ax_height + hgap, ax_width, ax_height])

        #To assign a left align --> align = 'edge', and use positive valued width
        #To assign a right align --> align = 'edge', and use negative valued width
        #To assign a center align --> align = 'center'
        
        ax1 = fig.add_subplot(2,1,1) #Plot with: 2 rows, 1 column, first subplot
        ax1.bar(before_numbers, before_array, label = 'Before', align = 'edge', width = 0.3, color = 'darkblue')
        ax1.bar(after_numbers, after_array, label = 'After', align = 'center', width = 0.3, color = 'lightblue')
        ax1.bar(ideal_numbers, ideal_array, label = 'Ideal', align = 'edge', width = -0.3, color = 'lightgreen')
        ax1.legend(loc = 'upper left')
        plt.subplots_adjust(bottom = 0.15, left = 0.15)
        plt.title("\nMSG Alarm Mesages - Optimization Results\n\n")
        plt.ylabel('% Efficiency ')
        x_upper_limit = len(numbers) + 20
        plt.xlim([-1, x_upper_limit])
        y_upper_limit = max([max(before_array), max(after_array), max(ideal_array)]) + 50
        plt.ylim([0, y_upper_limit])
        plt.xticks(numbers, name_array, rotation = 90)
        plt.tick_params(labelsize = 12)

        
        ax2 = fig.add_subplot(2,1,2) #Plot with: 2 row, 1 column, second subplot
        net_numbers = [-0.4, 0, 0.4]
        net_ideal = 100
        net_outputs = [net_before, net_after, net_ideal]
        net_names = ["Before", "After", "Ideal"]
        bar_plot = ax2.bar(net_numbers, net_outputs, align = 'center', width = 0.2)
        #ax2.bar(net_numbers[0], net_before, label = 'Before', align = 'edge', width = 0.2, color = 'darkblue')
        #ax2.bar(net_numbers[1], net_after, label = 'After', align = 'center', width = 0.2, color = 'lightblue')
        #ax2.bar(net_numbers[2], 100, label = 'Ideal', align = 'edge', width = -0.2, color = 'lightgreen')
        bar_plot[0].set_color('darkblue')
        bar_plot[0].set_label('Before')
        
        bar_plot[1].set_color('lightblue')
        bar_plot[1].set_label('After')
        
        bar_plot[2].set_color('lightgreen')
        bar_plot[2].set_label('Ideal')

        ax2.legend(loc = 'upper left')
        plt.title("Total Improvement - Net Summary")
        plt.ylabel('% Efficiency ')
        y_upper_limit = max(net_before, net_after, net_ideal) + 50
        plt.ylim([0, y_upper_limit])
        plt.xticks(net_numbers, net_names)
        plt.tick_params(labelsize = 12)
        fig.patch.set_facecolor('white')

        #Show Improvement due to Optimization
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.4, 0.95, textstr, fontsize = 20, transform = ax1.transAxes,
                 verticalalignment = 'top', bbox=props)
        #Get the three output bar graph rectangles (Before, After, and Ideal)
        rects = ax2.patches

        #For each bar: Place a label
        for rect in rects:
            #Get X and Y placement of label from rect.
            y_value = rect.get_height()
            x_value = rect.get_x() + rect.get_width()/2

            #Number of points between bar and label. Change to your liking.
            space = 5
            #Vertical alignment for positive values, at bottom of the label box
            va = 'bottom'

            #If value of bar is negative: Place label before bar (shouldn't ever happen, just in case though)
            if y_value < 0:
                #Invert space to place label below
                space *= -1
                #Vertically align label at top of label box
                va = 'top'
            #Use Y Value as label, and format number with two decimal places
            label = "{:.2f}".format(y_value)
            
            #Create Annotation
            plt.annotate(
                label,                          #Use 'label' as label text
                (x_value, y_value),             #Place label at end of the bar
                xytext = (0,space),             #Vertically shift label by 'space'
                textcoords ='offset points',    #Interpret 'xytext' as offset in points
                ha = 'center',                  #Horizontally center label
                va=va)                          #Positive and Negative values

        #Option to automatically save the results of the Graph (Script)
        if(automatic_graph_output == True):            
            #date = datetime.datetime.now()
            #date_format = str(date.strftime("%Y%m%d %Hh%Mmin"))
            #plt.savefig(python_output_directory + '\Alarm Message Summary _' + date_format +'.png')
            plt.savefig(python_output_directory + '\Alarm Message Summary _ Individual.png')
        plt.show()
        return
   
    def plotting(self, before_efficiency, after_efficiency):
        global automatic_graph_output
        global python_output_directory
        
        #Convert before and after efficiency to Percent Improvement, to 2 decimal places
        #textstr = '%.2f'%( 100 * abs(after_efficiency - before_efficiency) / float(before_efficiency) )
        textstr = '%.2f' %(before_efficiency - after_efficiency)
        textstr = "Improvement: " + textstr + "%"

        names = [1, 2, 3]
        ideal_efficiency = 100
        values = [before_efficiency, after_efficiency, ideal_efficiency]

        fig = plt.figure(1, figsize = (6,7))

        ax1 = fig.add_subplot(1,1,1)
        bar_plot = plt.bar(names, values, align = 'center', width = 0.5)
        
        #ax = fig.add_subplot(1,1,1)
        #ax.bar(names, values, align = 'center', width = 0.5)
        my_xticks = ["Before", "After", "Ideal"]
        plt.xticks(names, my_xticks)
        plt.title("\nMSG Alarm Mesages - Optimization Results\n\n")
        plt.ylabel('% Efficiency ')
        bar_plot[0].set_color('darkblue')
        bar_plot[1].set_color('lightblue')
        bar_plot[2].set_color('lightgreen')
        fig.patch.set_facecolor('white')
        y_upper_limit = max(before_efficiency, after_efficiency, ideal_efficiency) + 10
        plt.ylim([0, y_upper_limit])
        
        #Return the array containing the bar graph objects (each rectangle is a separate object)
        rects = ax1.patches

        #For each bar: Place a label
        for rect in rects:
            #Get X and Y placement of label from rect.
            y_value = rect.get_height()
            x_value = rect.get_x() + rect.get_width()/2

            #Number of points between bar and label. Change to your liking.
            space = 5
            #Vertical alignment for positive values, at bottom of the label box
            va = 'bottom'

            #If value of bar is negative: Place label before bar (shouldn't ever happen, just in case though)
            if y_value < 0:
                #Invert space to place label below
                space *= -1
                #Vertically align label at top of label box
                va = 'top'
            #Use Y Value as label, and format number with two decimal places
            label = "{:.2f}".format(y_value)
            
            #Create Annotation
            plt.annotate(
                label,                          #Use 'label' as label text
                (x_value, y_value),             #Place label at end of the bar
                xytext = (0,space),             #Vertically shift label by 'space'
                textcoords ='offset points',    #Interpret 'xytext' as offset in points
                ha = 'center',                  #Horizontally center label
                va=va)                          #Positive and Negative values

        #Meaning: transform = ax.transAxes, setting (0,0) as the bottom left of the figure, and (1,1) as the top right
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.25, 1.06, textstr, fontsize = 14, transform = ax1.transAxes, 
                verticalalignment = 'top', bbox=props)

        #Option to automatically save the results of the Graph (Script)
        if(automatic_graph_output == True):
            #date = datetime.datetime.now()
            #date_format = str(date.strftime("%Y%m%d %Hh%Mmin"))
            #plt.savefig(python_output_directory + '\Alarm Message Summary _' + date_format +'.png')
            plt.savefig(python_output_directory + '\Alarm Message Summary _ Combined.png')
        plt.show()
        return       
    

def main():

    message1 = Reorganize(input_directory)
    output_path_exists = message1.createFolder(python_output_directory)
    message1.createFolder(MSG_output_directory)
    message1.createFolder(temp_MSG_output_directory)
        
    message1.setOutputDirectory(output_path_exists, python_output_directory)
    message1.generateFileList("yes")
    message1.copyFiles("yes")
    #message1.printFields()
    message1.locateMSGFiles()
    message1.choose_calc_optimization()

if __name__ == "__main__":
    pass
    #main()


class MessageGUI:

    def __init__(self, master):
        
        global global_version
        global input_directory
        global MSG_file_order
        global config_file_name
        
        master.title("MSG Alarm Message Optimizer")
        master.resizable(False, False)

        #Configure Frame Styles for the GUI
        self.style = ttk.Style()
        self.style.configure('TFrame')
        self.style.configure('Main.TFrame', background = '#FFFFE0') #Yellow colour
        self.style.configure('Settings.TFrame', background = '#F0F0F0') #Blue colour - #b0e2ff, '#C5E3F7'
        self.style.configure('Bottom.TFrame', background = '#FFCDD2') #Red colour
        self.style.configure('Top.TFrame', background = '#FDFEFE') #White colour 

        #Configure Button Styles for the GUI
        self.style.configure('TButton')
        self.style.configure('Main.TButton', background = '#b0e2ff')
        self.style.configure('Settings.TButton', background = '#FFFFE0') 
        self.style.configure('Directory.TButton', background = '#85C1E9', font = ('Arial', 11, 'bold')) #Grey colour #EAECEE
        self.style.configure('Reset.TButton', background = '#EAECEE', font = ('Arial', 11)) #Grey colour
        self.style.configure('Bottom.TButton', background = '#EAECEE', font = ('Arial', 11, 'bold')) #Grey colour
        self.style.configure('Config.TButton', background = '#EAECEE', font = ('Times New Roman', 11, 'bold'))
        self.style.configure('Run.TButton', background = '#85C1E9', font = ('Arial', 14, 'bold'))
        self.style.configure('PlainBottom.TButton', background = '#EAECEE', font = ('Arial',12))

        #Configure TLabel Styles for the GUI
        self.style.configure('TLabel', font=('Arial', 11))
        self.style.configure('MainHeader.TLabel', font = ('Arial',12, 'bold'), background = '#FFFFE0')
        self.style.configure('MainLabel.TLabel', font = ('Arial',11), background = '#FFFFE0')
        self.style.configure('SettingsHeader.TLabel', font = ('Arial',12,'bold'), background = '#F0F0F0') #b0e2ff, #C5E3F7 
        self.style.configure('SettingsUnderline.TLabel', font = ('Arial', 11), background = '#b0e2ff')
        self.style.configure('Bottom.TLabel', font = ('Arial',2), background = '#FFCDD2')
        self.style.configure('Top.TLabel', font = ('Arial',11, 'bold'), background = '#FDFEFE')
        self.style.configure('Italic.TLabel', font = ('Arial', 10, 'italic'), background = '#FDFEFE')
        self.style.configure('Spacer.TLabel', font = ('Arial',6, 'bold'), background = '#FFFFE0')
        self.style.configure('Smallspacer.TLabel', font = ('Arial',2, 'bold'), background = '#FFFFE0')
        
        #Configure TRadiobutton Style for the GUI
        self.style.configure('MainHeader.TRadiobutton', font= ('Arial', 11), background = '#FFFFE0')
        self.style.configure('SettingsHeader.TRadiobutton', font = ('Arial', 11), background = '#F0F0F0') #'#b0e2ff', #C5E3F7

        #Configure Checkbutton Style for the GUI
        self.style.configure('TCheckbutton', font = ('Arial', 11), background = '#FFFFE0')
        self.style.configure('Main.TCheckbutton', font = ('Arial', 11), background = '#FFFFE0')
        self.style.configure('Settings.TCheckbutton', font = ('Arial', 11), background = '#F0F0F0') #C5E3F7 
        
        #Configure Text field Style for GUI
        
        #Text Toolbox
        self.white_space = "            "
        
        ###########################################################################s
        ### TOP FRAME                                                           ###
        ###########################################################################
        self.top_frame = ttk.Frame(master,style = 'Top.TFrame')
        self.top_frame.pack(side=TOP, fill=BOTH)
        self.top_frame.config(relief=RIDGE)
        self.top_frame.config(padding = (5,5))
        self.title_label = ttk.Label(self.top_frame, text = "MSG Alarm Messages Optimizer", style = 'Top.TLabel').grid(row = 0, column = 0, sticky = 'w')
        self.version_label = ttk.Label(self.top_frame, text = self.white_space + "Version: " + str(global_version), style = 'Italic.TLabel')
        self.version_label.grid(row = 0, column = 1)
        self.version_label.config(justify = RIGHT)

        ###########################################################################
        ### BOTTOM FRAME                                                        ###
        ###########################################################################
        self.bottom_frame = ttk.Frame(master, style = 'Bottom.TFrame')
        self.bottom_frame.pack(side = BOTTOM, fill = X)
        self.bottom_frame.config(relief = RIDGE)
        self.bottom_frame.config(padding = (5,5))

        ###########################################################################
        ### NOTEBOOK - Adds "Tabs" to the GUI                                   ###
        ###########################################################################
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(side = BOTTOM)

        ###########################################################################
        ### MAIN FRAME                                                          ###
        ###########################################################################
        self.main_frame = ttk.Frame(self.notebook, style = 'Main.TFrame')
        self.main_frame.pack(side = LEFT)
        self.main_frame.config(relief = RIDGE)
        self.main_frame.config(padding = (5,5))

        ###########################################################################
        ### SETTINGS FRAME                                                      ###
        ###########################################################################
        self.settings_frame = ttk.Frame(self.notebook, style = "Settings.TFrame")
        self.settings_frame.pack(side = RIGHT)
        self.settings_frame.config(relief = RIDGE)
        self.settings_frame.config(padding= (5,5))

        ###########################################################################
        ### NOTEBOOK - Configurations                                           ###
        ###########################################################################
        self.notebook.add(self.main_frame, text = "  Main  ")
        self.notebook.add(self.settings_frame, text = "Settings")
        self.notebook.tab(1, state = 'normal')

        ###########################################################################
        ### MAIN FRAME - Individual Components                                  ###
        ###########################################################################
        
        ###########################################################################
        #(1) Input File Directory (Main Frame)
        ###########################################################################
        self.input_directory_frame = ttk.Frame(self.main_frame, style = 'Main.TFrame')
        self.input_directory_frame.pack(fill=BOTH)
        self.input_directory_frame.config(relief = RIDGE)
        self.input_directory_frame.config(padding = (5,5))

        self.input_directory_label = ttk.Label(self.input_directory_frame, text = "Input - MSG File Directory", style = 'MainHeader.TLabel')
        self.input_directory_label.grid(row = 0, column = 0, padx = 0, sticky = 'w')

        self.input_directory_var = StringVar()
        self.input_directory_field = ttk.Entry(self.input_directory_frame, width = 100, font = ('Arial', 10), textvariable = self.input_directory_var)
        self.input_directory_field.grid(row = 1, column = 0, padx = 5, pady= 2)
        self.input_directory_field.insert(0, input_directory) #Set default value to the MSG File Directory
        
        self.input_directory_button = ttk.Button(self.input_directory_frame, text = "Change Input Directory", style = 'Directory.TButton')
        self.input_directory_button.grid(row = 2, column = 0, columnspan = 1, sticky = 'w', ipadx = 30)
        self.input_directory_button.config(command = self.choose_directory)

        self.default_directory_button = ttk.Button(self.input_directory_frame, text = "Reset Directory", style = 'Reset.TButton')
        self.default_directory_button.grid(row = 2, column = 0, columnspan = 1, sticky = "w", padx = 240, ipadx = 15)
        self.default_directory_button.config(command = self.set_default_directory)

        self.input_directory_label = ttk.Label(self.input_directory_frame, text = " ", style = 'Spacer.TLabel')
        self.input_directory_label.grid(row = 3, column = 0, padx = 0, sticky = 'w')

        ###########################################################################
        #(2) Graph Output Options (Main Frame)
        ###########################################################################
        self.output_graph_frame = ttk.Frame(self.main_frame, style = 'Main.TFrame')
        self.output_graph_frame.pack(fill=BOTH)
        self.output_graph_frame.config(relief = RIDGE)
        self.output_graph_frame.config(padding = (5,5))

        self.output_graph_label = ttk.Label(self.output_graph_frame, text = "Graph Output Options", style = 'MainHeader.TLabel')
        self.output_graph_label.grid(row = 0, column = 0, padx = 0, sticky = 'w')

        self.output_graph_val = IntVar()
        
        self.output_graph_auto= ttk.Radiobutton(self.output_graph_frame, text = '(Default) Automatically Save Output Graph',
            variable = self.output_graph_val, value = 0, style = 'MainHeader.TRadiobutton').grid(row = 1, column = 0, sticky = 'nsew')
        self.output_graph_no_auto = ttk.Radiobutton(self.output_graph_frame, text = "Manually Save Graph",
            variable = self.output_graph_val, value = 1, style = 'MainHeader.TRadiobutton').grid(row = 2, column = 0, sticky = 'nsew')

        self.input_directory_label = ttk.Label(self.output_graph_frame, text = " ", style = 'Spacer.TLabel')
        self.input_directory_label.grid(row = 3, column = 0, padx = 0, sticky = 'w')
                                        
        ###########################################################################
        #(3) Output File Directory (Main Frame)
        ###########################################################################
        
        self.output_directory_frame = ttk.Frame(self.main_frame, style = 'Main.TFrame')
        self.output_directory_frame.pack(fill=BOTH)
        self.output_directory_frame.config(relief = RIDGE)
        self.output_directory_frame.config(padding = (5,5))

        self.output_directory_label = ttk.Label(self.output_directory_frame, text = "Output Directory", style = 'MainHeader.TLabel')
        self.output_directory_label.grid(row = 0, column = 0, padx = 0, sticky = 'w')

        self.output_directory_var = StringVar()
        self.output_directory_field = ttk.Entry(self.output_directory_frame, width = 100, font = ('Arial', 10), textvariable = self.output_directory_var)
        self.output_directory_field.grid(row = 1, column = 0, padx = 5, pady= 2)
        self.output_directory_field.insert(0, python_output_directory) #Set default value to the Python Current Working Directory

        self.output_directory_button = ttk.Button(self.output_directory_frame, text = "Change Output Directory", style = 'Directory.TButton')
        self.output_directory_button.grid(row = 2, column = 0, columnspan = 1, sticky = 'w', ipadx = 25)
        self.output_directory_button.config(command = self.set_output_directory)
        
        self.reset_output_directory_button = ttk.Button(self.output_directory_frame, text = "Reset Directory", style = 'Reset.TButton')
        self.reset_output_directory_button.grid(row = 2, column = 0, columnspan = 1, sticky = 'w', padx = 240, ipadx = 15)
        self.reset_output_directory_button.config(command = self.reset_output_directory)

        self.input_directory_label = ttk.Label(self.output_directory_frame, text = " ", style = 'Spacer.TLabel')
        self.input_directory_label.grid(row = 3, column = 0, padx = 0, sticky = 'w')
        
        ###########################################################################
        #(4) Run Optimization Buttons (Main Frame)
        ###########################################################################
        
        self.start_optimization_frame = ttk.Frame(self.main_frame, style = 'Bottom.TFrame')
        self.start_optimization_frame.pack(fill = BOTH)
        self.start_optimization_frame.config(relief = RIDGE)
        self.start_optimization_frame.config(padding = (5,5))

        #self.output_directory_label = ttk.Label(self.start_optimization_frame, text = " ", style = 'Bottom.TLabel')
        #self.output_directory_label.grid(row = 0, column = 0, padx = 10, pady = 1, sticky = 'w')
        
        self.run_optimization_button = ttk.Button(self.start_optimization_frame, text = "Run Optimization", style = 'Run.TButton')
        self.run_optimization_button.grid(row = 0, column = 0, rowspan = 2, sticky = 'w', ipadx = 25, ipady = 5, padx = 9)
        self.run_optimization_button.config(command = self.run_optimization)

        self.open_output_folder = ttk.Button(self.start_optimization_frame, text = "Open Results Directory", style = 'Bottom.TButton')
        self.open_output_folder.grid(row = 0, column = 0, rowspan = 2, sticky = 'w', padx = 240, ipadx = 5, ipady = 5)
        self.open_output_folder.config(command = self.open_result_folder)
        
        self.open_results_file = ttk.Button(self.start_optimization_frame, text = "Open Message File", style = 'Bottom.TButton')
        self.open_results_file.grid(row = 0, column = 0, rowspan = 2, sticky = 'e', padx = 70, ipadx = 5, ipady = 5)
        self.open_results_file.config(command = self.open_output_message_file)

        self.save_configuration_button = ttk.Button(self.start_optimization_frame, text = "Save Settings", style = 'Config.TButton')
        self.save_configuration_button.grid(row = 0, column = 1, pady = 2, ipadx = 5, ipady = 5, sticky = 'n')
        #self.save_configuration_button.config(command = pass)

        self.reset_configuration_button = ttk.Button(self.start_optimization_frame, text = "Reset Settings", style = 'Config.TButton')
        self.reset_configuration_button.grid(row = 1, column = 1, pady = 2, ipadx = 5, ipady = 5, sticky = 's')
        #self.reset_configuration_button.config(command = pass)

        #self.output_directory_label = ttk.Label(self.start_optimization_frame, text = " ", style = 'Bottom.TLabel')
        #self.output_directory_label.grid(row = 3, column = 0, padx = 10, pady = 1, sticky = 'w')
        
        #############################################################################
        ### SETTINGS FRAME - Individual Components                                  #
        #############################################################################
        
        #############################################################################
        #(1) Set MSG File Order (Settings Frame)                                    #
        #############################################################################
        self.file_order_frame = ttk.Frame(self.settings_frame, style = 'Settings.TFrame')
        self.file_order_frame.pack(fill=BOTH)
        self.file_order_frame.config(relief= RIDGE)
        self.file_order_frame.config(padding = (5,5))

        self.file_order_select = IntVar()
        self.file_order_label = ttk.Label(self.file_order_frame, text = '(1) Set "MSG File Order"', style = "SettingsHeader.TLabel")
        self.file_order_label.grid(row = 0, column = 0, sticky = 'w')

        self.alphabet_file_order = ttk.Radiobutton(self.file_order_frame, text = '(Default) Alphabetic MSG File Order',
            variable = self.file_order_select, value = 0, style = 'SettingsHeader.TRadiobutton').grid(row = 1, column = 0, sticky = 'nsew')
        self.specific_file_order = ttk.Radiobutton(self.file_order_frame, text = 'Specific MSG File Order (In field below; Do not include MSG File Version)',
            variable = self.file_order_select, value = 1, style = 'SettingsHeader.TRadiobutton').grid(row = 2, column = 0, sticky = 'nsew')
        
        #self.MSG_file_order_field = ttk.Entry(self.file_order_frame, width = 100, font = ('Arial', 10), textvariable = self.MSG_file_order_var)
        #self.MSG_file_order_field.grid(row = 3, column = 0, sticky = 'e', padx = 5, pady= 2)
        #self.MSG_file_order_field.insert(0, MSG_file_order) #Set default value to the Python Current Working Directory        

        self.MSG_file_order_var = StringVar()
        self.MSG_file_order_field = Text(self.file_order_frame, width = 100, height = 3, font = ('Arial', 10, 'bold'))#, textvariable = self.MSG_file_order_var)
        self.MSG_file_order_field.grid(row = 3, column = 0, padx = 5, pady = 2)
        self.MSG_file_order_field.insert(1.0, display_MSG_file_order)

        self.reset_MSG_order_button = ttk.Button(self.file_order_frame, text = "Default File Order", style = 'Directory.TButton')
        self.reset_MSG_order_button.grid(row = 4, column = 0, columnspan = 1, sticky = 'w', ipadx = 5)
        self.reset_MSG_order_button.config(command = self.default_MSG_file_order)

        self.clear_MSG_order_button = ttk.Button(self.file_order_frame, text = "Clear All", style = 'Reset.TButton')
        self.clear_MSG_order_button.grid(row = 4, column = 0, columnspan = 1, sticky = 'w', padx = 150, ipadx = 5)
        self.clear_MSG_order_button.config(command = self.clearFileOrder)

        self.temp_save_MSG_order_button = ttk.Button(self.file_order_frame, text = 'Use Above File Order', style = 'Reset.TButton')
        self.temp_save_MSG_order_button.grid(row= 4, column = 0 , columnspan = 1, sticky = 'e', padx = 160, ipadx = 5)
        self.temp_save_MSG_order_button.config(command = self.tempSaveMSGFileOrder)

        self.save_to_config_MSG_button = ttk.Button(self.file_order_frame, text = 'Save to Config File', style = 'Directory.TButton')
        self.save_to_config_MSG_button.grid(row = 4, column = 0, columnspan = 1, sticky = 'e', ipadx = 5)
        self.save_to_config_MSG_button.config(command = self.configSaveMSGFileOrder)

        #(1) When open up script, it should try to find the configuration file, if it exists,
        #set the MSG_file_order variable to the array/dictionary order in the file
        #Top of file should have a set of instructions
        #parse through the file until the information is found!
        #When click: save_MSG_order_button --> updates the configuration file with the contents (if not found, it will create the file!)
        
        #############################################################################
        #(2) MSG File Analysis (Settings Frame)
        #############################################################################

        self.analysis_type_frame = ttk.Frame(self.settings_frame, style = 'Settings.TFrame')
        self.analysis_type_frame.pack(fill=BOTH)
        self.analysis_type_frame.config(relief= RIDGE)
        self.analysis_type_frame.config(padding = (5,5))

        self.file_order_label = ttk.Label(self.analysis_type_frame, text = "(2) MSG File Analysis", style = "SettingsHeader.TLabel")
        self.file_order_label.grid(row = 0, column = 0, sticky = 'w')

        self.analysis_type_var = IntVar()
        self.independent_file_analysis = ttk.Radiobutton(self.analysis_type_frame, text = 'Independent Analysis MSG Files',
            variable = self.analysis_type_var, value = 0, style = 'SettingsHeader.TRadiobutton').grid(row = 1, column = 0, sticky = 'nsew')
        self.combined_file_analysis = ttk.Radiobutton(self.analysis_type_frame, text = 'Combined Analysis MSG Files (uses: "MSG File Order")',
            variable = self.analysis_type_var, value = 1, style = 'SettingsHeader.TRadiobutton').grid(row = 2, column = 0, sticky = 'nsew')

        #############################################################################
        #(3) List of Input and Output MSG Files (Settings Frame)                    #
        #############################################################################
        
        self.input_output_files_frame = ttk.Frame(self.settings_frame, style = 'Settings.TFrame')
        self.input_output_files_frame.pack(fill=BOTH)
        self.input_output_files_frame.config(relief= RIDGE)
        self.input_output_files_frame.config(padding = (5,5))

        self.input_output_label = ttk.Label(self.input_output_files_frame, text = "(3) Input/Output File List (Troubleshooting purposes)", style = "SettingsHeader.TLabel")
        self.input_output_label.grid(row=0, column = 0, sticky = 'w')

        self.input_file_checkbox_var = IntVar()
        self.input_file_checkbox = ttk.Checkbutton(self.input_output_files_frame, text = "Generate list of Input MSG Files (.csv)", style = 'Settings.TCheckbutton')
        self.input_file_checkbox.grid(row = 1, column = 0, sticky = 'w')
        self.input_file_checkbox.config(variable = self.input_file_checkbox_var, onvalue = 1, offvalue = 0)

        self.output_file_checkbox_var = IntVar()
        self.output_file_checkbox = ttk.Checkbutton(self.input_output_files_frame, text = "Generate list of Output MSG Files (.csv)", style = 'Settings.TCheckbutton')
        self.output_file_checkbox.grid(row = 2, column = 0, sticky = 'w')
        self.output_file_checkbox.config(variable = self.output_file_checkbox_var, onvalue = 1, offvalue = 0)

        #############################################################################
        #(4) Automatically generate MSG File Output (Settings Frame)                #
        #############################################################################
        
        self.auto_gen_MSG_frame = ttk.Frame(self.settings_frame, style = 'Settings.TFrame')
        self.auto_gen_MSG_frame.pack(fill = BOTH)
        self.auto_gen_MSG_frame.config(relief = RIDGE)
        self.auto_gen_MSG_frame.config(padding = (5,5))

        self.auto_gen_MSG_file_label = ttk.Label(self.auto_gen_MSG_frame, text = "(4) Auto Generate MSG Files with Optimized Alarm Messages",
            style = "SettingsHeader.TLabel")
        self.auto_gen_MSG_file_label.grid(row = 0, column = 0, sticky = 'w')
        
        self.auto_gen_checkbox_var = IntVar()
        self.auto_gen_checkbox = ttk.Checkbutton(self.auto_gen_MSG_frame, text = "Automatically Generate MSG Files (Experimental)", style = 'Settings.TCheckbutton')
        self.auto_gen_checkbox.grid(row = 1, column = 0, sticky = 'w')
        self.auto_gen_checkbox.config(variable = self.auto_gen_checkbox_var, onvalue = 1, offvalue = 0)
    
    def update_variables(self):
        global automatic_graph_output
        global file_independent
        global message_independent
        global generate_input_file_list
        global generate_output_file_list
        global automatic_MSG_output
        
        #(1) Option - Automatic Graph Output
        if(self.output_graph_val.get() == 0):
            automatic_graph_output = True
        elif (self.output_graph_val.get() == 1):
            automatic_graph_output = False

        #(1) Set MSG File Order
        if(self.file_order_select.get() == 0):
            file_independent = 1
        elif(self.file_order_select.get() == 1):
            file_independent = 0
                       
        #(2) MSG File Analysis and Message Optimization
        #Independent Message Analysis of MSG Files
        if(self.analysis_type_var.get() == 0):
            message_independent = 1
        #Combined Message Analysis of MSG Files
        elif(self.analysis_type_var.get() == 1):
            message_independent = 0

        #(3) Input/Output File List
        #Input MSG File List (.csv)
        if(self.input_file_checkbox_var.get() == 1):
            generate_input_file_list = True
        elif(self.input_file_checkbox_var.get() == 0):
            generate_input_file_list = False
        #Output MSG File List (.csv)
        if(self.output_file_checkbox_var.get() == 1):
            generate_output_file_list = True
        elif(self.output_file_checkbox_var.get() == 0):
            generate_input_file_list = False
         
        #(4) Auto Generate MSG Files with Optimized Alarm messages incorporated
        #Generate MSG Files with Optimized Alarm Messages
        if(self.auto_gen_checkbox_var.get() == 1):
            automatic_MSG_output = True
        #Do not generate MSG Files
        elif(self.auto_gen_checkbox_var.get() == 0):
            automatic_MSG_output = None
        return
    
    def correctDirectoryName(self, input_string):
        input_string = input_string.replace('//',"\\")
        input_string = input_string.replace('/', "\\")
        return input_string
    
    def directoryInput(self):
        directory = tkFileDialog.askdirectory()
        if directory == None:
            return ""
        print directory
        return directory
    
    def choose_directory(self):
        global input_directory
        directory = self.directoryInput()  
        if (directory == "" or directory == None):
            print input_directory
            return
        else:
            input_directory = directory
            self.input_directory_field.delete(0,'end')
            self.input_directory_field.insert(0, input_directory)
            print self.input_directory_var.get()
            return
    
    def set_default_directory(self):
        global hard_coded_input_directory
        self.input_directory_var.set(hard_coded_input_directory)
        return

    def set_output_directory(self):
        global python_output_directory
        directory = self.directoryInput()
        if (directory == "" or directory == None):
            print python_output_directory
            return
        else:
            python_output_directory = directory
            self.output_directory_field.delete(0,'end')
            self.output_directory_field.insert(0, python_output_directory)
            print self.output_directory_var.get()
            return

    def open_result_folder(self):
        global python_output_directory
        corrected_directory = self.correctDirectoryName(python_output_directory)
        print "Python Output Directory: ", corrected_directory
        subprocess.call("explorer " + corrected_directory)
        return

    def open_output_message_file(self):
        global message_file
        corrected_directory = self.correctDirectoryName(message_file)
        print "Message File Directory: ", corrected_directory
        subprocess.Popen([r'notepad.exe', corrected_directory])
        return
    
    def reset_output_directory(self):
        global hard_coded_python_output_directory
        global python_output_directory

        #Reset output field
        self.output_directory_var.set(hard_coded_python_output_directory)
        
        #Reset Python Variable Directory
        python_output_directory = hard_coded_python_output_directory
        return

    def default_MSG_file_order(self):
        global hard_coded_MSG_file_order
        self.MSG_file_order_field.delete(1.0, 'end')
        
        output_string = ""
        for element in hard_coded_MSG_file_order[:-1]:
            output_string += element + ", "

        output_string += hard_coded_MSG_file_order[-1]
        self.MSG_file_order_field.insert(1.0, output_string)
        return

    def clearFileOrder(self):
        self.MSG_file_order_field.delete(1.0, 'end')
        return

    def read_configuration_file(self):
        global config_file_name
        global MSG_file_name
        global start_of_list_flag
        global end_of_list_flag
        
        cwd = os.getcwd()
        config_file = cwd + "\\" + config_file_name

        list_flag = 0
        MSG_file_order_array = []
        
        input_file = open(config_file_name, "r")
        for num, line in enumerate(input_file):
            if ((list_flag == 0) and (start_of_list_flag in line)):
                list_flag = 1
                continue
            elif((list_flag == 1) and (end_of_list_flag in line)):
                list_flag = 2
                break
            elif(list_flag == 1):
                MSG_file_order_array.append(line)
                continue

        #Close Configuration File
        input_file.close()
        
        #Remove white-space characters
        MSG_file_order_array = [element.strip() for element in MSG_file_order_array]

        #Set MSG File Name
        MSG_file_name = MSG_file_order_array
        return
            
    def tempSaveMSGFileOrder(self):
        global MSG_file_order
        header_string = "Temporarily Update MSG File Order"
        body_string = [' MSG File Order has been sucessfully updated!'
        '\n\nThis order will be lost if the script is restarted.'
        ' If you wish to permanently update the MSG File Order, please use:'
        ' \n"Save to Config File" Button.']
        confirmation = tkMessageBox.showinfo(header_string,body_string[0])

        #Format Text Field in GUI into String that can be written to Configuration File
        text_field_content = self.MSG_file_order_field.get(1.0, END)

        #Convert Text Field into Array
        text_field_array = text_field_content.split(",")

        #Remove white-space characters
        text_field_array = [element.strip() for element in text_field_array]

        #Automatically update the Radiobutton
        self.file_order_select.set(1)

        #####################################################
        #Update MSG_file_order for Message Optimization     #
        #####################################################    
        MSG_file_order = text_field_array
        return

    def configSaveMSGFileOrder(self):      
        global config_file_name
        global MSG_file_order
        global start_of_list_flag
        global end_of_list_flag
        text_field_string = ""

        header_string = "Saving Configuration"
        body_string = ['Do you want to OVERWRITE the old configuration file with'
        ' this new one?\n\nIf you choose YES, the MSG File Order will be SAVED. It will be automatically'
        ' loaded the next time the application is opened.']
        
        #Double check if user wants to over-write the old configuration file
        confirmation = tkMessageBox.askyesno(header_string,body_string[0])
        if(confirmation == False):
            return

        #Get Configuration File Path
        cwd = os.getcwd()
        config_file = cwd + "\\" + config_file_name

        #Format Text Field in GUI into String that can be written to Configuration File
        text_field_content = self.MSG_file_order_field.get(1.0, END)

        #Convert Text Field into Array
        text_field_array = text_field_content.split(",")

        #Remove white-space characters
        text_field_array = [element.strip() for element in text_field_array]

        #####################################################
        #Update MSG_file_order for Message Optimization     #
        #####################################################    
        MSG_file_order = text_field_array
        
        #Convery Array into String
        for element in text_field_array:
            text_field_string += element + "\n"

        with open (config_file, 'r') as f:
            text = f.readlines()

        #Find location in the file to change (first occurance of trigger "identifier_line")
        text_location = None
        for num, line in enumerate(text):
            if(start_of_list_flag in line):
                text_location = num
                break
        
        #Add New List at the Start Flag in the configuration file
        if (text_location is not None):
            text[text_location] += text_field_string + end_of_list_flag

        #Write Back to the File
        with open(config_file, "w") as f:
            f.writelines(text[:text_location+1])

        #Automatically update the Radiobutton
        self.file_order_select.set(1)
        return
      
    def run_optimization(self):
        global input_directory
        global python_output_directory
        global MSG_output_directory
        global temp_MSG_output_directory

        ############################################################
        ### Update Variables based up settings selected in GUI     #
        ############################################################
        self.update_variables()
        
        #############################################################
        ## Close previous MatPlotLib Plot                           #
        #############################################################
        plt.close()
        
        ############################################################
        ### Run the components of the script to Optimize Messages  #
        ############################################################
        input_directory = self.input_directory_var.get()
        message1 = Reorganize(input_directory)
        output_path_exists = message1.createFolder(python_output_directory)
        message1.createFolder(MSG_output_directory)
        message1.createFolder(temp_MSG_output_directory)
            
        message1.setOutputDirectory(output_path_exists, python_output_directory)
        message1.generateFileList("yes")
        message1.copyFiles("yes")
        #message1.printFields() #Don't need to uncomment
        message1.locateMSGFiles()
        message1.choose_calc_optimization()
        return

### Run the GUI
root = Tk()
messageGUI = MessageGUI(root)
root.mainloop()

            
        
