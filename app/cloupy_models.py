class FileObject:
    def __init__(self):
        self.name = ""
        self.appPath = ""
        self.fullPath = ""
        self.id = -1
        self.hash = ""


class JobObject:
    def __init__(self):
        self.id = -1
        self.fileObjectId = -1
        self.creationDate = ""
        self.status = "undefined"


class ResultsObject:
    def __init__(self):
        self.id = -1
        self.jobObjectId = -1
        self.creationDate = ""
        self.resultPath = ""
