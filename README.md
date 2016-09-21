# RocketChat-Python-API
Rocket Chat Python API library

# Requirements
 * Python 3
 * urllib3
 * pandas
 * json

# Usage

make sure you are using python 3
install requirement with `sudo pip3 install -r requirements.txt`


```
import RocketChatAPI

R = RocketChatAPI("ROCKET_CHAT_URL", 'USER', 'PASSWORD')

# to get public room listing
R.Get_Public_Room()

# To get messages in a room, required ROOM_ID
R.Get_Messages(ROOM_ID,SKIP,LIMIT)

# Join a room
R.Join_Room(ROOM_ID)

# Leave a room
R.Leave_Room(ROOM_ID)

# Send messages
R.Send_Message(ROOM_ID, "This is an awesome messages !")

# To create a new channel
R.Create_Channel(CHANNEL_NAME)

# Meta funtion to grab all message of an instance
R.Get_all_messages_as_df()

# Whe  you are finished don't forget to log out
R.Logout()
```
