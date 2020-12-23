from datetime import datetime
import cloupy_models
import subprocess
import hashlib
import sqlite3
import random
import string
import os


class ResultsObjectController:
    def createResults(jobId, resultString):
        resultsObjectInstance = cloupy_models.ResultsObject()
        resultsObjectInstance.id = DBController.createResultId()
        resultsObjectInstance.jobObjectId = jobId
        resultsObjectInstance.creationDate = JobObjectController.getCurrentTime()
        resultsObjectInstance.resultPath = ResultsObjectController.getFileNameForJob(jobId)
        ResultsObjectController.writeResultsToDisk(resultsObjectInstance, resultString)
        DBController.addResults(resultsObjectInstance.id, resultsObjectInstance.jobObjectId, resultsObjectInstance.creationDate, resultsObjectInstance.resultPath)
        return resultsObjectInstance

    def writeResultsToDisk(resultsObjectInstance, resultString):
        with open(resultsObjectInstance.resultPath, 'w') as fh:
            fh.write(resultString)

    def getFileNameForJob(jobId):
        name = JobObjectController.getFileObjectForJobId(jobId).fullPath
        return '.'.join([name.split('.')[0], "results"])

    def getResultString(resultsObjectInstance):
        with open(resultsObjectInstance.resultPath, 'r') as fh:
            resultString = fh.read()
        return resultString

    def getResultsObjectByName(partialPath):
        attributes = DBController.getResultObjectByResultPartialPath(partialPath)
        resultsObjectInstance = cloupy_models.ResultsObject()
        resultsObjectInstance.id = attributes[0]
        resultsObjectInstance.jobObjectId = attributes[1]
        resultsObjectInstance.creationDate = attributes[2]
        resultsObjectInstance.resultPath = attributes[3]
        return resultsObjectInstance


class JobObjectController:
    def getCurrentTime():
        return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))

    def createJob(fileId):
        jobObjectInstance = cloupy_models.JobObject()
        jobObjectInstance.fileObjectId = fileId
        jobObjectInstance.id = DBController.createJobId()
        jobObjectInstance.creationDate = JobObjectController.getCurrentTime()
        jobObjectInstance.status = "pending"
        DBController.addJob(jobObjectInstance.id, jobObjectInstance.fileObjectId, jobObjectInstance.creationDate, jobObjectInstance.status)
        return jobObjectInstance

    def getFileObjectForJobId(jobId):
        fileId = DBController.getFileIdForJobId(jobId)
        fileObjectInstance = FileObjectController.getFileObjectById(fileId)
        return fileObjectInstance

    def updateJob(jobObjectInstance, status):
        jobObjectInstance.status =  status
        DBController.updateJobStatusById(jobObjectInstance.id, jobObjectInstance.status)
        return jobObjectInstance

    def runFile(fileObjectInstance, jobObjectInstance):
        JobObjectController.updateJob(jobObjectInstance, "running")
        results = JobObjectController.runPythonFile(fileObjectInstance.fullPath)
        JobObjectController.updateJob(jobObjectInstance, "complete")
        resultsObjectInstance = ResultsObjectController.createResults(jobObjectInstance.id, results)
        return resultsObjectInstance

    def runPythonFile(path):
        return subprocess.check_output(str("python3 " + path).split()).decode()


class FileObjectController:
    def createFileObject(name, uploadFolder):
        fileObjectInstance = cloupy_models.FileObject()
        fileObjectInstance.name = FileObjectController.createRandomFileName(name,6)
        fileObjectInstance.appPath = os.path.join(uploadFolder, fileObjectInstance.name)
        fileObjectInstance.fullPath = os.path.realpath(fileObjectInstance.appPath)
        return fileObjectInstance

    def createFileHash(fileObjectInstance):
        fileObjectInstance.hash = FileObjectController.hashFile(fileObjectInstance.fullPath)
        return fileObjectInstance

    def writeFileToDisk(fileObjectInstance, flaskRequestFileObject):
        flaskRequestFileObject.save(fileObjectInstance.appPath)

    def writeFileToDB(fileObjectInstance):
        id = DBController.createFileId()
        DBController.addFile(id, fileObjectInstance.name, fileObjectInstance.fullPath, fileObjectInstance.appPath, fileObjectInstance.hash)

    def removeFileFromDisk(fileObjectInstance):
        os.remove(fileObjectInstance.fullPath)

    def getFileObjectById(fileId):
        attributes = DBController.getFileById(fileId)
        fileObjectInstance = cloupy_models.FileObject()
        fileObjectInstance.name = attributes[1]
        fileObjectInstance.appPath = attributes[3]
        fileObjectInstance.fullPath = attributes[2]
        fileObjectInstance.id = attributes[0]
        fileObjectInstance.hash = attributes[4]
        return fileObjectInstance

    def getFileObjectByName(name):
        hash = DBController.getFileHashByName(name)
        fileObjectInstance = FileObjectController.getFileObjectByHash(hash)
        return fileObjectInstance

    def getFileObjectByHash(hash):
        id = DBController.getFileIdByHash(hash)
        fileObjectInstance = FileObjectController.getFileObjectById(id)
        return fileObjectInstance

    def getRandomCharacter():
        c  = random.choice(string.printable)
        while (c in string.whitespace or c in string.punctuation):
            c  = random.choice(string.printable)
        return c

    def createRandomFileName(n, x):
        ext = n.split('.')[-1]
        name = ""
        for i in range(0,x):
            name += FileObjectController.getRandomCharacter()
        return  name + '.' + ext

    def hashFile(fileName):
        hash = hashlib.sha256()
        with open(fileName, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                hash.update(data)
        return hash.hexdigest()


class DBController:
    def querySelect(statement, attributes):
        dbConnection = sqlite3.connect('cloupy.db')
        dbCursor = dbConnection.cursor()
        dbCursor.execute(statement, attributes)
        results = dbCursor.fetchone()
        dbConnection.close()
        return results

    def querySelectAll(statement, attributes=None):
        dbConnection = sqlite3.connect('cloupy.db')
        dbCursor = dbConnection.cursor()
        if attributes is None:
            dbCursor.execute(statement)
        else:
            dbCursor.execute(statement, attributes)
        results = dbCursor.fetchall()
        dbConnection.close()
        return results

    def queryInsert(statement, attributes):
        dbConnection = sqlite3.connect('cloupy.db')
        dbCursor = dbConnection.cursor()
        dbCursor.execute(statement, attributes)
        dbConnection.commit()
        dbConnection.close()

    def queryUpdate(statement, attributes):
        dbConnection = sqlite3.connect('cloupy.db')
        dbCursor = dbConnection.cursor()
        dbCursor.execute(statement, attributes)
        dbConnection.commit()
        dbConnection.close()

    def createId(table, maxN=9999):
        ids = DBController.querySelectAll('SELECT ID FROM ' + table)
        id = random.randint(0,maxN)
        while id in ids:
            id = random.randint(0,maxN)
        return id

    def createResultId():
        return DBController.createId("RESULTS")

    def createFileId():
        return DBController.createId("FILES")

    def createJobId():
        return DBController.createId("JOBS")

    def addFile(fileId, fileName, filePath, fileAppPath, fileHash):
        attributes = (fileId, fileName, filePath, fileAppPath, fileHash,)
        DBController.queryInsert('INSERT INTO FILES (ID,FILENAME,FILEPATH,FILEAPPPATH,SHA256SUM) VALUES (?,?,?,?,?)', attributes)

    def addJob(jobId, fileId, creation, status):
        attributes = (jobId, fileId, creation, status,)
        DBController.queryInsert('INSERT INTO JOBS (ID,FILEID,CREATED,STATUS) VALUES (?,?,?,?)', attributes)

    def addResults(id, jobId, creation, resultPath):
        attributes = (id, jobId, creation, resultPath,)
        DBController.queryInsert('INSERT INTO RESULTS (ID,JOBID,CREATED,RESULTPATH) VALUES (?,?,?,?)', attributes)

    def checkFileHashExists(hash):
        attributes = (hash,)
        results = DBController.querySelect('SELECT ID FROM FILES WHERE SHA256SUM=?', attributes)
        return results is not None

    def getFileNameById(id):
        attributes = (id,)
        name = DBController.querySelect('SELECT FILENAME FROM FILES WHERE ID=?', attributes)[0]
        return name

    def getFileIdByHash(hash):
        attributes = (hash,)
        id = DBController.querySelect('SELECT ID FROM FILES WHERE SHA256SUM=?', attributes)[0]
        return id

    def getFileHashByName(name):
        attributes = (name,)
        hash = DBController.querySelect('SELECT SHA256SUM FROM FILES WHERE FILENAME=?', attributes)[0]
        return hash

    def getFileById(id):
        attributes = (id,)
        results = DBController.querySelect('SELECT ID, FILENAME, FILEPATH, FILEAPPPATH, SHA256SUM FROM FILES WHERE ID=?', attributes)
        return results

    def getFileIdForJobId(jobId):
        attributes = (jobId,)
        fileId = DBController.querySelect('SELECT FILEID FROM JOBS WHERE ID=?', attributes)[0]
        return fileId

    def getResultObjectByResultPartialPath(partialPath):
        attributes = ('%'+partialPath,)
        results = DBController.querySelect('SELECT ID, JOBID, CREATED, RESULTPATH FROM RESULTS WHERE RESULTPATH LIKE ?', attributes)
        return results

    def updateJobStatusById(jobId, status):
        attributes = (status, jobId,)
        DBController.queryUpdate('UPDATE JOBS SET STATUS=? WHERE ID=?', attributes)
