class Event(object):
    INSTANCE_EVENT = 'instance_event'
    TASK_EVENT = 'task_event'

    CONTROL = 'control'

    class Control:
        IDLE = 'idle'
        END_OF_PERIOD = 'end of period'

    def __init__(self, event_type, value, **kwargs):
        self.event_type = event_type
        self.value = value
        self.kwargs = kwargs
