import os, json, re
from notify import notification
#from crontab import CronTab
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler, PatternMatchingEventHandler

def load_config():
    with open("config.json") as conf:
        config = json.load(conf)

    if config['home'] == "":
        config['home'] = os.path.expanduser('~')
        with open("config.json", 'w') as f:
            json.dump(config, f, indent=4)

    return config

'''def setup_cron():
    with CronTab(user='root') as cron:
        job = cron.new(command='echo hello_world')
        job.minute.every(1)'''

def flatten_dict(dd, separator ='/', prefix =''):
    return { prefix + separator + k if prefix else k : v
            for kk, vv in dd.items()
            for k, v in flatten_dict(vv, separator, kk).items()
            } if isinstance(dd, dict) else { prefix : dd }

def get_key(dictionary, value):
    for key in dictionary:
        if isinstance(dictionary[key], list):
            for i in dictionary[key]:
                if i == value:
                    return key
        elif dictionary[key] == value:
            return key

def clean_paths(dictionary):
    dictionary = flatten_dict(dictionary)
    cleaned_paths = {}
    for path in dictionary:
        cleaned_paths['/'.join(path.split("/")[:-1])] = dictionary[path]
    return cleaned_paths

def move(source):    
    config = load_config()
    #print("retrieving regex paths")
    paths = flatten_dict(config['paths'])

    cleaned_paths = {}
    for path in paths:
        cleaned_paths['/'.join(path.split("/")[:-1])] = paths[path]
    paths = cleaned_paths

    #print("retrieving the regexs")
    regexs = []
    for path in paths:
        if isinstance(paths[path], list):
            for i in paths[path]:
                regexs.append(i)
        else:
            regexs.append(paths[path])
    #print(regexs)

    #print("checking file against config regexs")
    destination = ""
    for regex in regexs:
        if re.search(regex, source):
            destination = get_key(paths, regex)
            break
    if destination == "":
        return
    print("regex matched, moving file")

    file = source.split("/")[-1]
    destination = f'{config["home"]}/{destination}/{file}'
    print(destination)

    try:
        os.rename(source, destination)
        if config['notify_on_move']:
            notification(f"moved {file} to {destination}", "organizer")
    except FileNotFoundError as e:
        if config['debug_mode'] == "on":
            if config['debugging']['notify_on_error']:
                notification(f"{'/'.join(destination.split('/')[:-1])} not found", "organizer error")
            if config['debugging']['log_error']:
                with open("error.log", 'a') as f:
                    f.write(f"{str(e)}\n")

def on_created(event):
    print(f"\nhey, {event.src_path} has been created!")
    move(event.src_path)


if __name__ == "__main__":

    config = load_config()

    if config['automake_missing_folders']:
        paths = config['paths']
        paths = clean_paths(paths)
        paths = list(paths.keys())
        print(paths)
        for path in paths:
            dirs = path.split('/')
            for i in range(len(dirs)):
                try:
                    os.mkdir(f"{config['home']}/{'/'.join(dirs[0:i+1])}")
                except FileExistsError:
                    pass

    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    my_event_handler = RegexMatchingEventHandler([".+"], ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created

    path = os.path.expanduser('~')
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    my_observer.start()
    
    try:
        user = input("")
        my_observer.stop()
        my_observer.join()
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()


    # abandoned attempt
    '''def get_regex_paths(dictionary, regex_paths = {}, level=0):
        keys = list(dictionary.keys())
        if len(keys) >= 1:
            for key in keys:
                if type(dictionary[key]) == dict:
                    level += 1
                    k,v,l = get_regex_paths(dictionary[key], regex_paths, level)

                    if v in regex_paths:
                        regex_paths[v].append(k)
                    else:
                        regex_paths[v] = [k]

                    if l > 0:
                        l-=1
                        return key, v, l
                    elif l==0:
                        regex_paths[v].append(key)
                else:
                    level-=1
                    return key, dictionary[key], level
        return regex_paths'''
                    