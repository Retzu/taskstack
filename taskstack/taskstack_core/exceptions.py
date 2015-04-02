class QueueFullException(Exception):
    """Thrown when somebody tried to add a task to an already full queue"""
    pass

