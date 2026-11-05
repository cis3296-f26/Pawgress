import time
import database as db

class TimeTracker:

    #hashmap will hold user_id -> (hours studied, timer [null if stopped, time started if started])
    hashmap = {}
    def __init__(self):
        pass

    def timer_start(self, user_id):
        if str(user_id) in self.hashmap:
            if(self.hashmap[str(user_id)][1] == 0):
                self.hashmap[str(user_id)] = (self.hashmap[str(user_id)][0], time.time())
                return 0
            else:
                print("invalid start")
                return 1
        else:
            self.hashmap[str(user_id)] = (0, time.time())
            return 0

    async def timer_stop(self, user_id):
        if str(user_id) in self.hashmap:
            if self.hashmap[str(user_id)][1] != 0:
                self.hashmap[str(user_id)] = (self.hashmap[str(user_id)][0] + (time.time() - self.hashmap[str(user_id)][1]), 0)
                print(self.hashmap[str(user_id)][0])
                #add reward of coins to user account here
                await db.add_coins(10, user_id)
                return 0
            else:
                print("invalid stop")
                return 1
        else:
            print("doesn't exist")
            return 2

    def get_time(self, user_id):
        if str(user_id) in self.hashmap:
            return f"{int(self.hashmap[str(user_id)][0] // 60)} minutes"
        else:
            return str("It's so over, man. Just give up.")

    def is_running(self, user_id):
        entry = self.hashmap.get(str(user_id))
        return bool(entry) and entry[1] != 0

    def get_seconds(self, user_id):
        entry = self.hashmap.get(str(user_id))
        return entry[0] if entry else 0
