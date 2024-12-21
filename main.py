from datetime import datetime
from dotenv import load_dotenv
import lupa
from lupa import LuaRuntime
import os
import re
current_path = os.path.dirname(os.path.abspath(__file__))

class EPGP_DB():
    def __init__(self):
        self._roster_info = None
        self._snapshot_time = None
        self._log = None
        self._base_gp = None
        self._decay_p = None
        self._min_ep = None
        self._extras_p = None

    @property
    def roster_info(self):
        return self._roster_info
    @roster_info.setter
    def roster_info(self,value):
        self._roster_info = value
    @roster_info.deleter
    def roster_info(self):
        del self._roster_info

    @property
    def snapshot_time(self):
        return self._snapshot_time
    @snapshot_time.setter
    def snapshot_time(self,value):
        self._snapshot_time = value
    @snapshot_time.deleter
    def snapshot_time(self):
        del self._snapshot_time

    @property
    def log(self):
        return self._log
    @log.setter
    def log(self,value):
        self._log = value
    @log.deleter
    def log(self):
        del self._log

    @property
    def base_gp(self):
        return self._base_gp
    @base_gp.setter
    def base_gp(self,value):
        self._base_gp = value
    @base_gp.deleter
    def base_gp(self):
        del self._base_gp

    @property
    def decay_p(self):
        return self._decay_p
    @decay_p.setter
    def decay_p(self,value):
        self._decay_p = value
    @decay_p.deleter
    def decay_p(self):
        del self._decay_p

    @property
    def min_ep(self):
        return self._min_ep
    @min_ep.setter
    def min_ep(self,value):
        self._min_ep = value
    @min_ep.deleter
    def min_ep(self):
        del self._min_ep

    @property
    def extras_p(self):
        return self._extras_p
    @extras_p.setter
    def extras_p(self,value):
        self._extras_p = value
    @extras_p.deleter
    def extras_p(self):
        del self._extras_p

load_dotenv()
backup_dir = os.environ.get("backup_dir")
old_backup = os.environ.get("old_backup")
new_backup = os.environ.get("new_backup")
guild_name = os.environ.get("guild_name")

if backup_dir == None:
    backup_dir = current_path

old_main_dict = {}
main_dict = {}
alts_dict = {}
changes_ep = {}
changes_gp = {}
time_warning = []
kicked_or_leaved_characters_with_logs = []

lua = LuaRuntime(unpack_returned_tuples=True)

def time_to_human_readable(timestamp):
    time = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    return(time)

def get_info_from_file(backup_name,guild_name):
    epgp_db = EPGP_DB()
    with open(backup_dir+'/'+backup_name, 'r', encoding='utf-8') as fh:
        txt = fh.read()
    table = lua.eval(txt.replace("EPGP_DB = ",""))
    epgp_db.roster_info=table.namespaces.log.profiles[guild_name].snapshot.roster_info
    epgp_db.snapshot_time=table.namespaces.log.profiles[guild_name].snapshot.time
    epgp_db.log = table.namespaces.log.profiles[guild_name].log
    guild_info = table.namespaces.log.profiles[guild_name].snapshot.guild_info
    epgp_db.base_gp = int(re.search(r'@BASE_GP:(\d+)', guild_info).group(1))
    epgp_db.decay_p = int(re.search(r'@DECAY_P:(\d+)', guild_info).group(1))
    epgp_db.min_ep = int(re.search(r'@MIN_EP:(\d+)', guild_info).group(1))
    epgp_db.extras_p = int(re.search(r'@EXTRAS_P:(\d+)', guild_info).group(1))
    return(epgp_db)

old_epgp_db = get_info_from_file(old_backup,guild_name)
new_epgp_db = get_info_from_file(new_backup,guild_name)

for subtable in new_epgp_db.roster_info.values():
    character_name, character_class, note = list(subtable.values())
    is_main = re.match(r"\d+.\d+", note)
    if is_main or note == "":
        main_dict[character_name] = note
    else:
        alts_dict[character_name] = note

for subtable in old_epgp_db.roster_info.values():
    character_name, character_class, note = list(subtable.values())
    is_main = re.match(r"\d+.\d+", note)
    if is_main or note == 0 or note == "":
        old_main_dict[character_name] = note

for subtable in new_epgp_db.log.values():
    time, ep_or_gp, name, description, cost = list(subtable.values())
    if time > old_epgp_db.snapshot_time:
        if name in main_dict:
            main_name = name
        elif name in alts_dict:
            main_name = alts_dict[name]
        else:
            kicked_or_leaved_characters_with_logs.append([time_to_human_readable(time), ep_or_gp, name, description, cost])
        if ep_or_gp == 'EP':
            if main_name not in changes_ep:
                changes_ep[main_name] = 0
            changes = changes_ep[main_name]
            changes = changes + int(cost)
            changes_ep[main_name] = changes
        else:
            if main_name not in changes_gp:
                changes_gp[main_name] = 0
            changes = changes_gp[main_name]
            changes = changes + int(cost)
            changes_gp[main_name] = changes

    if time == old_epgp_db.snapshot_time:
        time, ep_or_gp, name, description, cost = list(subtable.values())
        time_warning.append([time_to_human_readable(time), ep_or_gp, name, description, cost])

print("old backup: time "+time_to_human_readable(old_epgp_db.snapshot_time)+ " (filename: "+old_backup+")")
print("new backup: time "+time_to_human_readable(new_epgp_db.snapshot_time)+ " (filename: "+new_backup+")")

if len(time_warning) > 0:
    print("\nSome log entries was created in same time (in minutes) when created old backup. Correct analyze not guarantee:")
    for i in time_warning:
        print(i)
    print("")
else:
    print("")

for key in main_dict:
    try:
        old_note = old_main_dict[key]
        if (old_note != ""):
            old_ep = int(old_note.split(',')[0])
            old_gp = int(old_note.split(',')[1])
        else:
            old_ep = 0
            old_gp = 0
    except KeyError:
        old_ep = 0
        old_gp = 0
    new_note = main_dict[key]
    if (new_note != ""):
        new_ep = int(new_note.split(',')[0])
        new_gp = int(new_note.split(',')[1])
    else:
        new_ep = 0
        new_gp = 0
    if key not in changes_ep:
        if old_ep != new_ep:
            print(key+': EP value is warning old EP = '+str(old_ep)+' not equal new EP = '+str(new_ep)+' without changes in logs, diff = '+str(old_ep-new_ep))
    else:
        if ((old_ep + changes_ep[key]) != new_ep):
            print(key+': EP value is warning old EP = '+str(old_ep)+', changes = '+ str(changes_ep[key])+', new EP = '+str(new_ep)+', diff = '+str(old_ep+changes_ep[key]-new_ep))
            # print('/epgp ep '+key+' "Корекція '+time_to_human_readable(old_epgp_db.snapshot_time).split(' ')[0]+'" '+str(old_ep+changes_ep[key]-new_ep))
    if key not in changes_gp:
        if old_gp != new_gp:
            print(key+': GP value is warning old GP = '+str(old_gp)+' not equal new GP = '+str(new_gp)+' without changes in logs, diff = '+str(old_gp-new_gp))
    else:
        if ((old_gp + changes_gp[key]) != new_gp):
            print(key+': GP value is warning old GP = '+str(old_gp)+', changes = '+ str(changes_gp[key])+', new GP = '+str(new_gp)+', diff = '+str(old_gp+changes_gp[key]-new_gp))
            # print('/epgp gp '+key+' "Корекція '+time_to_human_readable(old_epgp_db.snapshot_time).split(' ')[0]+'" '+str(old_gp+changes_gp[key]-new_gp))

if len(kicked_or_leaved_characters_with_logs) > 0:
    print("\nSome characters are missing in the new guild roster, but present in new logs:")
    for i in kicked_or_leaved_characters_with_logs:
        print(i)
