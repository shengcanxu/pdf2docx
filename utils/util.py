from utils.logger import FileLogger
import json
import requests
import re


# write content to file in filepath
def write2File(filePath, content, mode="w+", encoding='utf8') -> bool:
    try:
        fp = open(filePath, mode=mode, encoding=encoding)
        fp.write(content)
        fp.flush()
        fp.close()
        return True
    except Exception as ex:
        FileLogger.error("write to file error on path: %s" % filePath)
        FileLogger.error(ex)
        return False


# read file from filePath
def readFile(filePath, encoding='utf8'):
    try:
        fp = open(filePath, mode='r', encoding=encoding)
        content = fp.read()
        return content
    except Exception as ex:
        FileLogger.error(ex)
        return False


# get json object from file
def getJsonFromFile(path):
    text = readFile(path)
    if text:
        jsonObjects = json.loads(text)
        return jsonObjects
    else:
        return []


# download file and save in folder
def downloadFile(url, filePath):
    try:
        r = requests.get(url)
        with open(filePath, "wb") as fp:
            fp.write(r.content)
    except Exception as ex:
        FileLogger.error("downloadfile error on path: %s" % url)
        FileLogger.error(ex)
        return False
