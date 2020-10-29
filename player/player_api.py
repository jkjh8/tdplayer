from pymongo import MongoClient


def api(data, db):    
    if data.startswith("returnip"):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        func, ip, port = data.split(',')

        db.setup.update_one({"_id": "1"}, { '$set': { 'rtIp': ip } })
        db.setup.update_one({"_id": "1"}, { '$set': { 'rtPort': int(port) } })
        return ('returnAddr,{},{}'.format(ip, port))
        
    elif data.startswith("fullscreen"):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'True' in data or 'true' in data:
            value = True
        else: value = False
        db.setup.update_one({"_id": "1"}, { '$set': { 'fullscreen': value }})
        return('fullscreen,{}'.format(value))
    
    elif data.startswith("poweronplay"):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'True' in data or 'true' in data:
            value = True
        else: value = False
        db.setup.update_one({"_id": "1"}, { '$set': { 'poweronplay': value }})
        return('poweronplay,{}'.format(value))

    elif data.startswith('loop_one'):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'true' in data or 'True' in data:
            value = True
        else: value = False
        db.setup.update_one({"_id": "1"}, { '$set': { 'loop_one': value } })
        return ('loop_one,{}'.format(value))

    elif data.startswith('loop'):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'true' in data or 'True' in data:
            value = True
        else: value = False
        db.setup.update_one({"_id": "1"}, { '$set': { 'loop': value } })
        return ('loop,{}'.format(value))

    elif data.startswith('progress'):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'true' in data or 'True' in data:
            value = True
        else: value = False
        db.setup.update_one({"_id": "1"}, { '$set': { 'progress': value } })
        return ('progress,{}'.format(value))

    elif data.startswith('endclose'):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'true' in data or 'True' in data:
            value = True
        else: value = False
        db.setup.update_one({"_id": "1"}, { '$set': { 'endclose': value } })
        return ('endclose,{}'.format(value))

    elif data == ("getlist"):
        playlist = db.playlist.find({},{ 'complete_name': 1, 'name': 1, 'type': 1, 'playid': 1, '_id': False })
        rtList = []
        for item in playlist:
            rtList.append(item['name'].replace("'",""))
        return ('getList,{}'.format(','.join(rtList)))

    elif data == ("getlist_full"):
        playlist = db.playlist.find({},{ 'complete_name': 1, 'name': 1, 'type': 1, 'playid': 1, '_id': False })
        rtList = []
        for item in playlist:
            rtList.append("{}.{}".format(item['name'], item['type']).replace("'",""))
        return ('getlist_full,{}'.format(','.join(rtList)))

    elif data == ("getaudiolist"):
        playlist = db.playlist.find(
            { '$or': [{'type': 'mp3'}, {'type': 'wav'}] },
            { 'complete_name': 1, 'name': 1, 'type': 1, 'playid': 1, '_id': False })
        rtList = []
        for item in playlist:
            rtList.append(item['name'].replace("'",""))
        return ('getaudiolist,{}'.format(','.join(rtList)))

    elif data == ("getaudiolist_full"):
        playlist = db.playlist.find(
            { '$or': [{'type': 'mp3'}, {'type': 'wav'}, {'type': 'flac'}, {'type': 'aac'}] },
            { 'complete_name': 1, 'name': 1, 'type': 1, 'playid': 1, '_id': False })
        rtList = []
        for item in playlist:
            rtList.append("{}.{}".format(item['name'], item['type']).replace("'",""))
        return ('getaudiolist_full,{}'.format(','.join(rtList)))

    elif data == ("getvideolist"):
        playlist = db.playlist.find(
            { '$or': [{'type': 'mp4'}, {'type': 'wmv'}, {'type': 'mov'}, {'type': 'avi'}, {'type': 'mpeg'}, {'type': 'asf'}] },
            { 'complete_name': 1, 'name': 1, 'type': 1, 'playid': 1, '_id': False })
        rtList = []
        for item in playlist:
            rtList.append(item['name'].replace("'",""))
        return ('getvideolist,{}'.format(','.join(rtList)))

    elif data == ("getvideolist_full"):
        playlist = db.playlist.find(
            { '$or': [{'type': 'mp4'}, {'type': 'wmv'}, {'type': 'mov'}, {'type': 'avi'}, {'type': 'mpeg'}, {'type': 'asf'}] },
            { 'complete_name': 1, 'name': 1, 'type': 1, 'playid': 1, '_id': False })
        rtList = []
        for item in playlist:
            rtList.append("{}.{}".format(item['name'], item['type']).replace("'",""))
        return ('getvideolist_full,{}'.format(','.join(rtList)))

    elif data == ("getfilelist"):
        filelist = db.filelist.find({},{ 'complete_name': 1, 'name': 1, 'type': 1, 'playid': 1, '_id': False })
        rtList = []
        for item in filelist:
            rtList.append(item['name'].replace("'",""))
        return ('getfilelist,{}'.format(','.join(rtList)))

    elif data == ("getfilelist_full"):
        filelist = db.filelist.find({},{ 'complete_name': 1, 'name': 1, 'type': 1, 'playid': 1, '_id': False })
        rtList = []
        for item in filelist:
            rtList.append("{}.{}".format(item['name'], item['type']).replace("'",""))
        return ('getfilelist_full,{}'.format(','.join(rtList)))

    else:
        return('unknown message')
