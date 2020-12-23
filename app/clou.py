from flask import Flask
from flask import request
from flask import send_from_directory
from cloupy_controllers import ResultsObjectController
from cloupy_controllers import FileObjectController
from cloupy_controllers import JobObjectController
from cloupy_controllers import DBController
from cloupy_models import FileObject


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '../uploads/'


@app.route('/', methods=['POST', 'GET'])
def input():
    if  request.method == 'GET':
        return "Use 'curl -X POST -F\"file=@/path/to/whatever\" localhost:5000/'"
    elif request.method == 'POST':
        return upload(request.files['file'])
    else:
        return "error"


@app.route('/view/<filename>')
def viewed_file(filename):
    try:
        resultsObjectInstance = ResultsObjectController.getResultsObjectByName(filename)
        resultString = ResultsObjectController.getResultString(resultsObjectInstance)
        data = resultString
    except:
        data = "File " + filename + " not found.\n"
    return data


@app.route('/run/<filename>')
def uploaded_file(filename):
    try:
        fileObjectInstance = FileObjectController.getFileObjectByName(filename)
        jobObjectInstance = JobObjectController.createJob(fileObjectInstance.id)
        resultsObjectInstance = JobObjectController.runFile(fileObjectInstance, jobObjectInstance)
        resultUrl = resultsObjectInstance.resultPath.split('/')[-1]
        data = "http://localhost:5000/view/"  + resultUrl +  '\n'
    except:
        data = "File " + filename + " not found.\n"
    return data


@app.route('/time')
def get_time():
    return JobObjectController.getCurrentTime()


def upload(flaskRequestFileObject):
    fileObjectInstance = FileObjectController.createFileObject(flaskRequestFileObject.filename, app.config['UPLOAD_FOLDER'])
    print("Adding " + fileObjectInstance.name + '.')
    FileObjectController.writeFileToDisk(fileObjectInstance, flaskRequestFileObject)
    fileObjectInstance = FileObjectController.createFileHash(fileObjectInstance)
    if DBController.checkFileHashExists(fileObjectInstance.hash):
        originalFileObjectInstance = FileObjectController.getFileObjectByHash(fileObjectInstance.hash)
        print(fileObjectInstance.name + " exists as " + originalFileObjectInstance.name + "; deleting the copy.")
        FileObjectController.removeFileFromDisk(fileObjectInstance)
        fileObjectInstance = originalFileObjectInstance
    else:
        FileObjectController.writeFileToDB(fileObjectInstance)
    return "http://localhost:5000/run/"  + fileObjectInstance.name +  '\n'
