from enum import IntEnum

from .race import racetime
from ..util import level


FIELD_UNKNOWN = int(-1)
LEVEL_UNKNOWN_DEATH = int(0)
LEVEL_FINISHED = int(-2)


class RacerStatus(IntEnum):
    unready = 1
    ready = 2
    racing = 3
    forfeit = 4
    finished = 5

StatusStrs = {RacerStatus.unready: 'Not ready.',
              RacerStatus.ready: 'Ready!',
              RacerStatus.racing: 'Racing!',
              RacerStatus.forfeit: 'Forfeit!',
              RacerStatus.finished: ''
              }

# Allowable transitions are:
#        unready <--> ready      (use ready() and unready())
#        ready    --> racing     (use begin_race())
#        racing  <--> forfeit    (use forfeit() and unforfeit())
#        racing  <--> finished   (use finish() and unfinish())


class Racer(object):
    def __init__(self, member):
        self.member = member                    # the Discord member who is this racer
        self._state = RacerStatus.unready       # see RacerState notes above
        self.time = FIELD_UNKNOWN               # hundredths of a second
        self.igt = FIELD_UNKNOWN                # hundredths of a second
        self.level = FIELD_UNKNOWN              # level of death (or LEVEL_FINISHED or LEVEL_UNKNOWN_DEATH)
        self.comment = ''                       # a comment added with .comment

    @property
    def name(self):
        return self.member.display_name

    @property
    def id(self):
        return int(self.member.id)

    @property
    def status_str(self):
        return self._status_str(False)

    @property
    def short_status_str(self):
        return self._status_str(True)
    
    def _status_str(self, short):
        status = ''
        if self._state == RacerStatus.finished:
            status += racetime.to_str(self.time)
            if not self.igt == -1 and not short:
                status += ' (igt {})'.format(racetime.to_str(self.igt))
        else:
            status += StatusStrs[self._state]
            if self._state == RacerStatus.forfeit and not short:
                status += ' (rta {}'.format(racetime.to_str(self.time))
                if 0 < self.level < 22:
                    status += ', ' + level.to_str(self.level)
                if not self.igt == -1:
                    status += ', igt {}'.format(racetime.to_str(self.igt))
                status += ')'

        if not self.comment == '' and not short:
            status += ': ' + self.comment

        return status

    @property
    def time_str(self):
        return racetime.to_str(self.time)

    @property
    def is_ready(self):
        return self._state == RacerStatus.ready

    @property
    def has_begun(self):
        return self._state > RacerStatus.ready

    @property
    def is_racing(self):
        return self._state == RacerStatus.racing

    @property
    def is_forfeit(self):
        return self._state == RacerStatus.forfeit

    @property
    def is_finished(self):
        return self._state == RacerStatus.finished

    @property
    def is_done_racing(self):
        return self._state > RacerStatus.racing

    def ready(self):
        if self._state == RacerStatus.unready:
            self._state = RacerStatus.ready
            return True
        return False

    def unready(self):
        if self._state == RacerStatus.ready:
            self._state = RacerStatus.unready
            return True
        return False

    def begin_race(self):
        if self._state == RacerStatus.ready:
            self._state = RacerStatus.racing
            return True
        return False

    def forfeit(self, time):
        if self._state == RacerStatus.racing or self._state == RacerStatus.finished:
            self._state = RacerStatus.forfeit
            self.time = time
            self.level = LEVEL_UNKNOWN_DEATH
            self.igt = FIELD_UNKNOWN
            return True
        return False

    def unforfeit(self):
        if self._state == RacerStatus.forfeit:
            self._state = RacerStatus.racing
            self.time = FIELD_UNKNOWN
            self.igt = FIELD_UNKNOWN
            self.level = FIELD_UNKNOWN
            return True
        return False

    def finish(self, time):
        if self._state == RacerStatus.racing or self._state == RacerStatus.forfeit:
            self._state = RacerStatus.finished
            self.time = time
            self.level = LEVEL_FINISHED
            return True
        return False
            
    def unfinish(self):
        if self._state == RacerStatus.finished:
            self._state = RacerStatus.racing
            self.time = FIELD_UNKNOWN
            self.igt = FIELD_UNKNOWN
            self.level = FIELD_UNKNOWN
            return True
        return False

    def add_comment(self, comment):
        self.comment = comment
