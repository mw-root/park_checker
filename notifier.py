import config
from pushbullet import Pushbullet
pb = Pushbullet(config.pb_api_key)

def push_note( msg, title = None ):
    push = pb.push_note(title or "Video Card In Stock!", msg)