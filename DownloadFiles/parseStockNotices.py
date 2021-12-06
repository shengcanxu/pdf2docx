##
# 从公告中读取信息并下载附件（如有）
##
import sys
sys.path.append("C:/project/Tushare")
from requests_html import HTMLSession
from utils.logger import FileLogger
import time
import json
import os.path
import pandas as pd
import numpy as np
from utils.util import getJsonFromFile, readFile, downloadFile


# get anual and quarterly report from notices and save to DB 
def retrieveAnualQuarterlyReport():
    stockList = getJsonFromFile("C:/project/stockdata/StockNotices/stock.json")
    stockList = stockList["stockList"]

    # stockList = [{"orgId":"9900002701","category":"A股","code":"002127","pinyin":"njds","zwjc":"南极电商"}]
    # stockList = [{"orgId":"gssz0000002","category":"A股","code":"000002","pinyin":"njds","zwjc":"万科A"}]

    for stock in stockList:
        FileLogger.info("running on stock: %s(%s)" % (stock["zwjc"], stock["code"]))
    
        try:
            filePath = "C:/project/stockdata/StockNotices/%s.json" % stock['code']
            jsonList = getJsonFromFile(filePath)

            annualDf = None
            for jsonObj in jsonList:
                announcementType = jsonObj['announcementType']
                fileType = jsonObj['adjunctType']

                # 得到公告类型，一季报半年报三季报年报
                # 公告类型：{'01030501': 第一季度报全文, '01030701':第三季度报, '01030301': 半年报, '01030101':年报全文}
                noticeType = None
                if announcementType.find("01030101") != -1: 
                    noticeType = "年报"
                elif announcementType.find("01030701") != -1:
                    noticeType = "三季度报"
                elif announcementType.find("01030301") != -1:
                    noticeType = "半年报"
                elif announcementType.find("01030501") != -1:
                    noticeType = "一季度报"

                if noticeType is not None and (fileType == 'PDF' or filePath == 'PDF ' or fileType == 'pdf'):
                    FileLogger.info("downloading file: %s" % jsonObj["announcementTitle"])
                    noticeDay = jsonObj['adjunctUrl'][10:20]
                    url = "http://www.cninfo.com.cn/new/announcement/download?bulletinId=%s&announceTime=%s" % (jsonObj['announcementId'], noticeDay)
                    
                    annualData = {
                        'code': jsonObj['secCode'],
                        'name': jsonObj['secName'],
                        'announcementId': jsonObj['announcementId'],
                        'title': jsonObj['announcementTitle'], 
                        'noticeDay': noticeDay,
                        'fileType': jsonObj['adjunctType'],
                        'url': url, 
                        'Type': noticeType, 
                        'year': int(noticeDay[0:4])-1 if noticeType == "年报" else int(noticeDay[0:4])
                    }
                    if annualDf is None:
                        annualDf = pd.DataFrame(columns=annualData.keys())
                        annualDf = annualDf.append(annualData, ignore_index=True)
                    else:
                        annualDf = annualDf.append(annualData, ignore_index=True)

            time.sleep(0)
        
            # save to DB
            from sqlalchemy import create_engine
            ENGINE = create_engine("mysql+pymysql://root:4401821211@localhost:3306/eastmoney?charset=utf8")
            annualDf.to_sql(name="reportbasic", con=ENGINE, if_exists="append")

        except Exception as ex:
            FileLogger.error(ex)
            FileLogger.error("retrieve error on code: %s" % stock["code"])
            time.sleep(3)


# 公告文件类型的数量:{'PDF': 4517872, None: 93056, 'TXT': 2223, 'DOC': 2, 'JPG': 3, '2': 1, '55': 1, 'PDF ': 208, 'pdf': 23}
if __name__ == "__main__":
# http://www.cninfo.com.cn/new/announcement/bulletin_detail?announceId=13519195&flag=true&announceTime=2004-01-17

    # retrieveAnualQuarterlyReport()

    stockdf = pd.read_csv("C:/project/stockdata/StockNoticesFile/annualreportlist.csv", dtype={'code': np.str, 'year': np.str})
    # stockdf = stockdf[stockdf['code'] == '000002']
    stockList = stockdf[['code', 'name', 'year', 'announcementId', 'url']].to_numpy()

    # stockList = stockList[1:3]
    
    try:
        for stock in stockList: 
            fileName = "[%s]%s年报-%s" % (stock[1], stock[2], stock[3])
            savePath = "C:/project/stockdata/StockNoticesFile/pdf_download/%s.pdf" % fileName
            # make sure it's a valid path, no \/:?*"<>|
            savePath = savePath.replace("*", "")
            unresolvedPath = "C:/project/stockdata/StockNoticesFile/unresolved/%s.pdf" % fileName

            url = stock[4]
            if os.path.exists(savePath) or os.path.exists(unresolvedPath):
                FileLogger.info("file %s exists, skip!" % fileName)
            else:
                FileLogger.info("downloading file: %s" % fileName)
                downloadFile(url, savePath) 

    except Exception as ex:
        FileLogger.error(ex)
        FileLogger.error("download error on file: %s" % fileName)
        time.sleep(3)
