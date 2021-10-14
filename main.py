import os, json, time
from notify import notification
#from crontab import CronTab
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

def load_config():
    with open("config.json") as conf:
        config = json.load(conf)
    if config['home'] == "":
        config['home'] = os.path.expanduser('~')
        with open("config.json", 'w') as conf:
            json.dump(config, conf, indent=4)
    return config

'''def setup_cron():
    with CronTab(user='root') as cron:
        job = cron.new(command='echo hello_world')
        job.minute.every(1)'''

def on_created(event):
    print(f"hey, {event.src_path} has been created!")

if __name__ == "__main__":

    patterns = ["*"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created

    path = "."
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    my_observer.start()
    
    while True:
        user = input("")
        if user == "exit":
            my_observer.stop()
            my_observer.join()
            break


    '''config = load_config()
    for i in os.listdir(f"{config['home']}/Downloads"):
        for pattern in config['paths'].keys():
            if pattern in i:
                try:
                    os.rename(f"{config['home']}/Downloads/{i}", f"{config['home']}/{config['paths'][pattern]}/{i}")
                    if config['notify_on_move']:
                        notification(f"moved {i} to {config['home']}/{config['paths'][pattern]}", "organizer")
                except FileNotFoundError as e:
                    if config['debug_mode'] == "on":
                        if config['debugging']['notify_on_error']:
                            notification(f"{config['home']}/{config['paths'][pattern]} not found", "organizer error")
                        if config['debugging']['log_error']:
                            with open("error.log", 'a') as f:
                                f.write(f"{str(e)}\n")'''
                    