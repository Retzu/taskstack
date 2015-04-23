"""Custom exceptions for taskstack"""


class QueueFullException(Exception):

    """Thrown when somebody tried to add a task to an already full queue"""


class UserAlreadyWorkingException(Exception):

    """Thrown when a member is told to work on a task when already working on one."""