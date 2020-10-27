import os
from pymediainfo import MediaInfo
from flask_pymongo import PyMongo

def FileMediaInfo(db, MEDIA_DIR):
    db.delete_many({})
    fileList = []
    fileNameList = os.listdir(MEDIA_DIR)
    for item in fileNameList:
        fileInfo = {}
        info = MediaInfo.parse(os.path.join(MEDIA_DIR,item)).tracks[0]
        fileInfo['name'] = info.file_name
        fileInfo['complete_name'] = info.complete_name
        fileInfo['type'] = info.file_extension
        fileInfo['size'] = info.file_size
        fileInfo['duration'] = info.duration
        fileList.append(fileInfo)
    db.insert_many(fileList)
    return list(db.find({}))