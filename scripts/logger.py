from datetime import datetime

def now():
    return datetime.strftime(datetime.now(), "%m-%d|%H:%M:%S ")

def log(s):
    try:
        with open("./logs.txt", "a") as file:
            file.write(now() + s + "\n")
        return 
    except:
        pass
