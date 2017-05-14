'''
Created on 05.05.2017

@author: David H Stocker

This utility will extract maplight contribution data for display in the html files in this repo.  
Maplight is an activist website dedicated to exposing how money affects US politcs.  The data 
from Maplight comes in turn from OpenSecrets.org

http://maplight.org/us-congress/contributions
https://www.opensecrets.org/

Data format is "Date","Amount","Recipient","Party","Office","District","District state","District number","Contributor","Interest Group","Occupation/Employer","City","State","Zip"
'''


#!/usr/bin/env python3

import os
import sys
import codecs
import json

global masterData
global detailData
global interestGroupIndex
interestGroupIndex = {"(All)" : 0}  #Interest group index acts as a "bridge" dict and its values act as shared "primary keys" in the master and detail dicts
masterData = {0 : {"id" : 0, "interestGroup" : "(All)", "amount" : 0}}  #Initializing the all bucket with 0
detailData = {0 : []}
aMasterData = []
aDetailData = []


    
if __name__ == "__main__":
    insertStatements = []
    try:
        #When the user elects to download the contributions of a single legislator, then it will be contained in a 
        #    comma separated values file, called contribuions.csv
        #Read it!
        sorceFileName = sys.argv[1]
        filePath = os.path.realpath(__file__)
        selfDir = os.path.dirname(filePath)
        dataLocation = os.path.join(selfDir, sorceFileName)
        readLoc = codecs.open(dataLocation, "r", "utf-8")
        allLines = readLoc.readlines()
        readLoc.close
        
        #Pull the congressman metadata from the first data row
        firstDataRow = allLines[1][1:-1]
        parsedFirstDataRow = firstDataRow.split("\",\"")
        recipient = parsedFirstDataRow[2]
        party = parsedFirstDataRow[3];
        district = parsedFirstDataRow[5];
        
        fileStringRecipient = 'headerText_Recipient = "%s";\n' %recipient
        fileStringParty = 'headerText_Party = "%s";\n' %party
        fileStringDistrict = 'headerText_District = "%s";\n' %district
        
        nthLine = 0
        for eachReadLine in allLines:
            try:
                if nthLine == 0:
                    pass # ignore the header row
                else:
                    eachReadLine = eachReadLine[1:-1]
                    parsedDataRow = eachReadLine.split("\",\"")
                    
                    #Dollar amounts carry a dollar sign and comma thousand separators.  Strip them and convert the string to an int
                    amount = parsedDataRow[1]
                    amount = amount.replace(',', '')
                    amount = amount.replace('$', '')
                    amount = int(amount)
                    amount = abs(amount)
                    
                    cdate = parsedDataRow[0]
                    contributor = parsedDataRow[8]
                    interestGroup = parsedDataRow[9]
                
                    #Update the data for the master table.  The (All) entry is at key 0
                    oldMasterTotaEntry = masterData[0]
                    oldMasterTotal = oldMasterTotaEntry["amount"]
                    newMasterTotal = oldMasterTotal + amount
                    masterData[0] = {"id" : 0, "interestGroup" : "(All)", "amount" : newMasterTotal}
                    
                    #Do we have an existing interest group, or does the line have a new one?
                    #  Either way, determine the appropriate id value
                    igID = len(interestGroupIndex)
                    if interestGroup in interestGroupIndex.keys():
                        igID = interestGroupIndex[interestGroup]
                
                        #Update existing master data total for the interest group
                        igMasterEntry = masterData[igID]
                        oldIGTotal = igMasterEntry["amount"]
                        newIGTotal = oldIGTotal + amount
                        newMasterRegistryEntry = {"id" : igID, "interestGroup" : interestGroup, "amount" : newIGTotal}
                        masterData[igID] = newMasterRegistryEntry
                        
                        #Update the data for the detail table entry for the interest group
                        igDetailEntry = detailData[igID]
                        newDetailLineItem = {"contributor" : contributor, "amount" : amount, "date" : cdate}
                        igDetailEntry.append(newDetailLineItem)
                        detailData[igID] = igDetailEntry
                    else:
                        #We need a new master index entry
                        interestGroupIndex[interestGroup] = igID
                        
                        #if it is not in already, then create a new dict entry
                        newMasterRegistryEntry = {"id" : igID, "interestGroup" : interestGroup, "amount" : amount}
                        masterData[igID] = newMasterRegistryEntry
                        
                        #Update the data for the detail table
                        newDetailLineItem = {"contributor" : contributor, "amount" : amount, "date" : cdate}
                        detailData[igID] = [newDetailLineItem]
                
                    #in either case (novel interest group, or already seen) case, we need to add newDetailLineItem to the (All) ig.
                    aigDetailEntry = detailData[0]
                    aigDetailEntry.append(newDetailLineItem)
                    detailData[0] = aigDetailEntry 
                                  
                nthLine = nthLine + 1    
            except Exception:
                pass
        
        #Format the master and detail data in a UI5 friendly JSON format
        masterDataJSON = json.dumps(masterData, indent=4)
        detailDataJSON = json.dumps(detailData, indent=4)
        fileStringMasterDataJSON = 'masterData = %s;\n' %masterDataJSON
        fileStringDetailDataJSON = 'detailDataAll = %s;\n' %detailDataJSON
        
        #write the data
        dataLocation = os.path.join(selfDir, "contribdata.js")
        writeLoc = codecs.open(dataLocation, "w", "utf-8")
        writeLoc.writelines([fileStringRecipient, fileStringParty, fileStringDistrict, fileStringMasterDataJSON, fileStringDetailDataJSON])
        writeLoc.close

    except Exception as e:
        raise e
    
    
    
    
    print("Done")
    
    
    """
                readRow(eachReadLine)        
        
        #For managing the type of upload
        loadFlag = "all"
        try:
            if sys.argv[4] == "metadata":
                loadFlag = "metadata"
                print("... loading metadata (including stations) only")
            elif sys.argv[4] == "data":
                loadFlag = "data"
                print("... loading fact table data only")
            else:
                print("... loading metadata (including stations) and fact table data")
        except:
            print("... loading metadata (including stations) and fact table data")

        #Read the files
        if (loadFlag == "all") or (loadFlag == "metadata"):
            flagData = WeatherData.getLoadFlags()
            stationData = WeatherData.getStations()
            insertStatements.extend(flagData)
            insertStatements.extend(stationData)
        if (loadFlag == "all") or (loadFlag == "data"):    
            factTableData = WeatherData.getDailyFiles()  
            insertStatements.extend(factTableData)  
            
        filePath = os.path.realpath(__file__)
        selfDir = os.path.dirname(filePath)
        dataLocation = os.path.join(selfDir, targetFileName)
        
        f = codecs.open( dataLocation, 'w', 'utf-8' )
        for l in insertStatements:
            f.write("%s;\n" % l)
        f.close
    
    """

