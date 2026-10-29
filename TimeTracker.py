import time

class TimeTracker:

    #hashmap will hold user_id -> (hours studied, timer [null if stopped, time started if started])
    hashmap = {}

    def __init__(self):
        pass

    def timer_start(self, user_id):
        if str(user_id) in self.hashmap:
            if(self.hashmap[str(user_id)][0] != 0):
                self.hashmap[str(user_id)] = (self.hashmap[str(user_id)][0], time.time())
            else:
                print("invalid")
        else:
            self.hashmap[str(user_id)] = (0, time.time())

    def timer_stop(self, user_id):
        if str(user_id) in self.hashmap:
            if self.hashmap[str(user_id)][1] != 0:
                self.hashmap[str(user_id)] = (self.hashmap[str(user_id)][0] + (time.time() - self.hashmap[str(user_id)][1]), 0)
                print(self.hashmap[str(user_id)][0])
            else:
                print("invalid")
        else:
            print("invalid")
