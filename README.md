# Message Buffer Optimizer

  This repository details an end-to-end optimization solution that was built for a real-time messaging system. The specific use-case has been redacted as it is superflucous to the exercise itself. Instead effort has been made to demonstrate fundamental principles of: computing and data structures, algorithmic thinking, basic compression, data visualization, user considerations, and automation.
  
 >**Please Note:** No raw files have been provided. All original details removed. What remains is the design structure, algorithm, python code, Tcl/Tk GUI, and data visualization. These have been provided for the hope that I will be able to share my learning with those on a similar path.

## Table of Contents
1) [Summary of Features](#summary-of-features)
2) [Python Dependencies](#python-dependencies)
3) [Optimization Algorithm](#optimization-technique)
4) [Message System](#simple-diagram-of-the-message-system)
5) [Algorithm Implementation](#implementation-of-message-optimization-algorithm)
6) [Optimization Tool](#optimization-tool)
7) [Data Visualization](#data-visualization-and-automation)
8) [Remarks](#remarks)

## Summary of Features

1) Reads input files from given directory, parses message element regions, ignores non-message space.
2) Computes current inefficiency of memory utilization (i.e. wasted character space and lines)
3) Optimizes current configuration (optimization is a local maximum)
4) Data Visualization - Displays plots comparing: Current Efficiency, Optimized Efficiency, and Perfect Memory Utilization
5) Automatically generates files with message elements in optimized configuration

## Python Dependencies
1) Written in **Python 2** and GUI built using Tcl/Tk (due to userbase, and legacy systems)
2) [Pandas](https://pypi.org/project/pandas/#files)
3) [Matplotlib](https://pypi.org/project/matplotlib/)

## Optimization Technique

  [Optimization](https://en.wikipedia.org/wiki/Mathematical_optimization) techniques are the means to select the best value with respect to a set of other available alternatives. In many practical cases, we seek to improve a value, parameter, path, or element or set of elements through manipulating a set of parameter(s). This optimization may involve maximizing, minimizing, or getting close to a specific reference point or metric. Examples of this involve ["hill climbing" algorithms](https://en.wikipedia.org/wiki/Hill_climbing), where one starts with an arbitary solution (that may or may not be optimial), and attempts to find a better solution through iterative changes. If the change results in improving the existing solution, then it is incorporated, and another change will be attempted. This process continues until: no further improvements can be made, the magnitude of those improvements become diminishingly small (example of diminishing returns), or the desired level of accuracy of optimization (sometimes called "error") is achieved. The technique accomplished by this tool performs a local search in a single pass. It does not search globally for a solution due to the exhaustive nature of that process. It was more important for this program to be run quickly and return a reasonably good solution, then take more time and perform a more thorough search to return the most optimial solution (e.g. global maximum). 
  
  The solution arrived at by this tool is a highly simplified 2D bin packing algorithm. The process of finding an optimial packing of items, each with their own weights, within a given space is classically referred to as the [knapsack problem](https://en.wikipedia.org/wiki/Knapsack_problem). 
>The knapsack problem or rucksack problem is a problem in combinatorial optimization: Given a set of items, each with a weight and a value, determine the number of each item to include in a collection so that the total weight is less than or equal to a given limit and the total value is as large as possible

### Simple Diagram of the Message System

<a href="url"><img src="https://github.com/Cabralcm/MemoryMessageOptimizer/blob/master/Images/Message_System.png" align="center" height="380" width="640" ></a>

   The memory buffer is a 2D array, where each line has a fixed character space, and contains messages. The messages are read from files, and are added to the memory buffer at run-time. The messages cannot span multiple lines. Messages must be added in order to the memory buffer. As such, there are cases where the message system must jump to a new line to order to add the next message, without fully utilzing the remaining space on the current line. The purpose of this python script is to reduce these occurances, and thus improve the ulitization of the memory buffer space. That is, better compress the messages into the buffer space, minimizing the amount of wasted space. Perfect ultilization is typicaly not possible (unless we have very special circumstances). 
   
   In order to optimize a given configuration, we first read in all the messages from the existing configuration, and try to build a new sequential configuration that descreases the number of wasted characters and lines.
   
   First use a Max Heap data structure to store all of the messages. We determine the remaining un-used space on a given line of the memory buffer, we will search through this Max Heap to find if there exists a message that is equal to or smaller than this remaining space. If so, remove it from the Max Heap, and add it to the **Optimized Configuration** of messages. Otherwise, continue to the next line and add the largest message from the Max Heap to the **Optimized Configuration**. The process ends when the Max Heap is empty.

The program then generates the optimized files, as well as generates a file showing the optimized message configuration (where each message is identified using ID numbers).

## Implementation of Message Optimization Algorithm 

### Example of a Disordered Message Configuration

<a href="url"><img src="https://github.com/Cabralcm/MemoryMessageOptimizer/blob/master/Images/Original_Message.PNG" align="center" height="460" width="500" ></a>

### Example of an Optimized Message Configuration

<a href="url"><img src="https://github.com/Cabralcm/MemoryMessageOptimizer/blob/master/Images/Optimized_Message.PNG" align="center" height="460" width="500" ></a>
 

## Optimization Tool

### Data Workflow

An end-to-end block diagram is outlined below illustrating the simple data processing pipeline. 

**Key considerations:**
 1) Local copy of input files are made instead of reading from production file repository
 2) Offers user both automatic and manual (suggested message order) methods of implementing the optimized memory configuration
 3) Data visualization shows improvement individually by file, and as a whole. Allowing for users to choose which files in production are worth changing.


<a href="url"><img src="https://github.com/Cabralcm/MemoryMessageOptimizer/blob/master/Images/Message_Optimization_Flow.PNG" align="center"></a>

### Main View

<a href="url"><img src="https://github.com/Cabralcm/MemoryMessageOptimizer/blob/master/Images/GUI_First.PNG" align="center"></a>
**Description**
 1) Input file directory
 2) Auto-save Optimization Data Visualization Plot
 3) Output Directory, contains:
   - optimized files
   - copied raw files 
   - message order list
   - data visualization plot

### Settings View

<a href="url"><img src="https://github.com/Cabralcm/MemoryMessageOptimizer/blob/master/Images/GUI_Second.PNG" align="center"></a>

**User Consideration**
Automatically generated optimized files are **not** activated default due to their processing time (approximately 1 minute). This enables the users to be able to first analyze the percent improvement offered by the optimization (via the data visualization plot), and then make a decision.

## Data Visualization and Automation
  In addition to the optimization function, this tool provides a clean data-visualization of **before** and **after** the optimization has taken place. This is useful to inform the extent of the optmization, demonstrate its value, as well determine its necessity. The input files are actively being worked on, and over time entropy may build, and the optimial configuration of the messages may drift, thus demonstrating that it is necessary to optimize the message buffer. Conversely, if the messages are in a reasonably good configuration, it may not be necessary to expend the effort to refactor the messages. The process of changing the message code in production is a highly involved process with many checks and balances, thus chaanges should only be undertaken if they pose a significant enough benefit.
  
<a href="url"><img src="https://github.com/Cabralcm/MemoryMessageOptimizer/blob/master/Images/Data_Vis.png" align="center"></a>


## Remarks

### Input File Structure
   As with any set of input that follows a fixed structure, there are symbols and identifiers for indicating different types of data. In our case we have simplified that into: *message* and *non-message* data. We will not be delving into this here, as it is tangential to the algorithm as a whole, but it is important to note that this tool is built to read in raw input files as actively utilized by the message system, and not merely cleaned up versions of the messages themselves. This provides an convenient means for the user to make use of this tool without significant work on their part.

### Final Comments

  Overall, this project was a joy to create, and a solo-effort, with lots of feedback from multiple users, engineers, and subject matter experts. From the onset of gathering technical requirements, learning and testing different optimization methods, iterative prototyping and development, and finally building a user interface (UI) as well as data visualization. The value in the data visualization is two-fold: (1) To help establish a business-case by presenting the value the optimization offers, (2) To asertain if the optimization is necessary at any given point in time. My hope is that the process of documenting this journey helps assist others who are trying to solve similar problems, and serve as a stepping stone for even more exciting software projects that delve into the beauty of software development, algorithms, and engineering. My best wishes to you.



