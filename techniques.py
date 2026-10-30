from itertools import cycle
import asyncio

class StudyTechnique:
    label = ""
    description = ""

    def schedule(self):
        raise NotImplementedError

class Pomodoro(StudyTechnique):
    label = "Pomodoro Study Method"
    description = "Study for 25 minutes, take a 5 minute break, then your 4th break is 15 minutes."

    PATTERN = [
        ("Focus", 25 * 60), ("Break", 5 * 60),
        ("Focus", 25 * 60), ("Break", 5 * 60),
        ("Focus", 25 * 60), ("Break", 5 * 60),
        ("Focus", 25 * 60), ("Break", 15 * 60),
    ]

    def schedule(self):
        return cycle(self.PATTERN)

class NinetyMinBlock(StudyTechnique):
    label = "90-Minute Focus Block Method"
    description = "Study for 90 minutes, then take a 20 minute break."

    PATTERN = [
        ("Focus", 90 * 60), ("Break", 20 * 60),
    ]

    def schedule(self):
        return cycle(self.PATTERN)

class Flowtime(StudyTechnique):
    label = "Flowtime Study Method"
    description = "Study however long you please, then take a proportional break :)"

    def schedule(self):
        yield "Focus", None

POMODORO = Pomodoro()
NINETY_MIN_BLOCK = NinetyMinBlock()
FLOWTIME = Flowtime()

class StudySession():
    def __init__(self, user, channel, technique, tracker):
        self.user = user
        self.channel = channel
        self.technique = technique
        self.tracker = tracker
        self._start_total = tracker.get_seconds(user.id)
        self._task = None

    def start(self):
        self._task = asyncio.create_task(self.run())

    async def run(self):
        schedule = self.technique.schedule()
        phase, seconds = next(schedule)
        announce = False
        while True:
            if phase == "Focus":
                self.tracker.timer_start(self.user.id)
            if announce:
                await self.channel.send(
                    f"{self.user.mention} {phase} time for {seconds // 60} minutes."
                )
            if seconds is None:
                return
            await asyncio.sleep(seconds)
            if phase == "Focus":
                self.tracker.timer_stop(self.user.id)
            phase, seconds = next(schedule)
            announce = True

    def stop(self):
        if self._task and not self._task.done():
            self._task.cancel()
        if self.tracker.is_running(self.user.id):
            self.tracker.timer_stop(self.user.id)
        studied = self.tracker.get_seconds(self.user.id) - self._start_total
        return int(studied // 60)