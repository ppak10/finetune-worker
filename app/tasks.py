from app import celery

@celery.task
def add(x, y):
    return x + y

@celery.task
def multiply(x, y):
    return x * y

@celery.task
def subtract(x, y):
    return x - y
