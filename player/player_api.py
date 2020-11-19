from pymongo import MongoClient

def api(data, setup, playlistGroup, filelist):
    if data.startswith("rtaddr,"):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        func, ip, port = data.split(',')

        setup.update_one({"_id": "1"}, { '$set': { 'rtIp': ip } })
        setup.update_one({"_id": "1"}, { '$set': { 'rtPort': int(port) } })
        return ('rtaddr,ip:{},port:{}'.format(ip, port))
        
    elif data.startswith("fs,"):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'True' in data or 'true' in data:
            value = True
        else: value = False
        setup.update_one({"_id": "1"}, { '$set': { 'fullscreen': value }})
        return('fs:{}'.format(value))
    
    elif data.startswith("pp,"):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'True' in data or 'true' in data:
            value = True
        else: value = False
        setup.update_one({"_id": "1"}, { '$set': { 'poweronplay': value }})
        return('pp:{}'.format(value))

    elif data.startswith('lo,'):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'true' in data or 'True' in data:
            value = True
        else: value = False
        setup.update_one({"_id": "1"}, { '$set': { 'loop_one': value } })
        return ('lo:{}'.format(value))

    elif data.startswith('la,'):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'true' in data or 'True' in data:
            value = True
        else: value = False
        setup.update_one({"_id": "1"}, { '$set': { 'loop': value } })
        return ('la:{}'.format(value))

    elif data.startswith('dr,'):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'true' in data or 'True' in data:
            value = True
        else: value = False
        setup.update_one({"_id": "1"}, { '$set': { 'progress': value } })
        return ('dr:{}'.format(value))

    elif data.startswith('ec,'):
        # currentdbId = db.setup.find_one({},{'_id': 1})
        if '1' in data or 'true' in data or 'True' in data:
            value = True
        else: value = False
        setup.update_one({"_id": "1"}, { '$set': { 'endclose': value } })
        return ('ec:{}'.format(value))

    elif data.startswith("gfl,"):
        playlist = list(filelist.find())
        rtList = []
        for item in playlist:
            rtList.append(item['name'].replace("'",""))
        return ('list:gfl,{}'.format(','.join(rtList)))

    elif data.startswith("gpl,"):
        gl = data.split(",", 1)
        playlist = list(playlistGroup[int(gl[1])].find())
        rtList = []
        for item in playlist:
            rtList.append(item['name'].replace("'",""))
        return ('list:gpl,{}'.format(','.join(rtList)))

    elif data.startswith("gpal,"):
        gl = data.split(",", 1)
        playlist = playlistGroup[int(gl[1])].find(
            { '$or': [{'type': 'mp3'}, {'type': 'wav'}, {'type': 'flac'}, {'type': 'aac'}] },
            { 'complete_name': 1, 'name': 1, 'type': 1, 'playid': 1, '_id': False })
        rtList = []
        for item in playlist:
            rtList.append(item['name'].replace("'",""))
        return ('list:gpal,{}'.format(','.join(rtList)))

    elif data.startswith("gpvl,"):
        gl = data.split(",", 1)
        playlist = playlistGroup[int(gl[1])].find(
            { '$or': [{'type': 'mp4'}, {'type': 'wmv'}, {'type': 'mov'}, {'type': 'avi'}, {'type': 'mpeg'}, {'type': 'asf'}] },
            { 'complete_name': 1, 'name': 1, 'type': 1, 'playid': 1, '_id': False })
        rtList = []
        for item in playlist:
            rtList.append(item['name'].replace("'",""))
        return ('list:gpvl,{}'.format(','.join(rtList)))
    else:
        return('unknown message')
