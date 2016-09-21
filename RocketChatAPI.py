import urllib3
import json
import pandas as pd


class RocketChatAPI:

    def __init__(self, baseurl, user, password):
        self.baseurl = baseurl
        self.headers = self.Login(user, password)

    def POST(self, url, fields={}, headers=None):
        if not headers:
            headers = self.headers
        http = urllib3.PoolManager()
        r = http.request(
            "POST", url,
            body=json.dumps(fields),
            headers=headers)
        try:
            d = json.loads(r.data.decode('utf8'))
        except:
            print(r.data)
        return d

    def GET(self, url, fields={}):
        http = urllib3.PoolManager()
        r = http.request(
            "GET", url,
            headers=self.headers)
        try:
            d = json.loads(r.data.decode('utf8'))
        except:
            print(r.data)
        return d

    def Login(self, user, password):
        url = self.baseurl + 'api/login'
        data = {"user": user,
                "password": password}

        headers = {'Content-Type': 'application/json'}
        d = self.POST(url, data, headers)
        userId = d['data']['userId']
        authToken = d['data']['authToken']
        headers = {
            "X-Auth-Token": authToken,
            "X-User-Id": userId
        }
        return headers

    def Logout(self):
        url = self.baseurl + "api/logout"
        d = self.GET(url)
        if d['status'] != 'success':
            print("Loged Out")
        else:
            return d

    def Get_Public_Room(self):
        url = self.baseurl + "api/publicRooms"
        d = self.GET(url)
        if d['status'] != 'success':
            print(d)
            raise("Error getting rooms list")
        else:
            return d

    def Join_Room(self, roomID):
        url = self.baseurl + "/api/rooms/" + roomID + "/join"
        d = self.POST(url)
        if d['status'] != 'success':
            print(d)
            raise("Error Joining the room")
        else:
            return True

    def Leave_Room(self, roomID):
        url = self.baseurl + "/api/rooms/" + roomID + "/leave"
        d = self.POST(url)
        if d['status'] != 'success':
            print(d)
            raise("Error Leaving the room")
        else:
            return True

    def Get_Messages(self, roomID, skip, limit):
        url = self.baseurl + "api/rooms/" + roomID + "/messages?skip=%s&limit=%s" % (skip, limit)
        d = self.GET(url)
        if d['status'] != 'success':
            print(d)
            raise("Error getting room messages")
        else:
            return d

    def Send_Message(self, roomID, message):
        url = self.baseurl + "api/rooms/" + roomID + "/send"
        data = "{ \"msg\" : \"OK\" }"
        headers = self.headers
#         headers["Content-Type"] = "application/json"
        d = self.POST(url, fields=data, headers=headers)
        if d['status'] != 'success':
            print(d)
            raise("Error sending message")
        else:
            return True

    def Create_Channel(self, channelName):
        url = self.baseurl + "api/v1/channels.create"
        data = {"name": channelName}
        d = self.POST(url, fields=data)
        if d['success'] is True:
            print(d)
            raise("Error Creeating Channel")
        else:
            return True

    def Get_all_messages_as_df(self):
        rooms_raw = self.Get_Public_Room()
        messages = {}
        rooms = []
        roomsid_name = {}
        userList = []
        for room in rooms_raw['rooms']:
            roomID = room['_id']
            if 'lm' in room.keys():
                lastmessage = room['lm']
            else:
                lastmessage = 'NaN'
            name = room['name']
            if 'topic' in room.keys():
                topic = room['topic']
            else:
                topic = ""
            creation = room['ts']
            if 'u' in room:
                creatorID = room['u']['_id']
                creator = room['u']['username']
            else:
                creator, creatorID = '', ''
            rooms.append([roomID, name, topic, creation, creatorID, creator, lastmessage])
            roomsid_name[roomID] = name
            for u in room['usernames']:
                userList.append([roomID, name, u])
            msgs = {'messages': []}
            msg = self.Get_Messages(roomID, 0, 50)
            msgs['messages'] += msg['messages']
            skip = 50
            while len(msg['messages']) == 50:
                msg = self.Get_Messages(roomID, skip, 50)
                msgs['messages'] += msg['messages']
                skip += 50
            messages[roomID] = msgs
        data = []
        for roomID in messages.keys():
            for msg in messages[roomID]['messages']:
                ts = msg['ts']
                userID = msg['u']['_id']
                user = msg['u']['username']
                if 't' in msg.keys():
                    t = msg['t']
                else:
                    t = 'None'
                data.append([roomID, roomsid_name[roomID], ts, userID, user, t])
        df = pd.DataFrame(data, columns=['roomID', 'roomName', 'timestamp', 'userID', 'userName', 't'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['ts'] = df['timestamp'].apply(lambda x: x.value)
        m = df['ts'].min()
        df['sec'] = df['timestamp'].apply(lambda x: (x.value - m) / 1e9)
        df['min'] = df['timestamp'].apply(lambda x: int((x.value - m) / 1e9 / 60))
        df['hour'] = df['timestamp'].apply(lambda x: int((x.value - m) / 1e9 / 3600))
        df['day'] = df['timestamp'].apply(lambda x: int((x.value - m) / 1e9 / 3600 / 60))
        return df
