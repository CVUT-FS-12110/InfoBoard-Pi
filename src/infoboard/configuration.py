import os
import uuid

import yaml
from crontab import CronTab
import psutil
import glob
import pathlib
import sh

def linux_block_devices():
    for blockdev_stat in glob.glob('/sys/block/*/stat'):
        blockdev_dir = blockdev_stat.rsplit('/', 1)[0]
        for part_stat in glob.glob(blockdev_dir + '/*/stat'):
            yield f'/dev/{part_stat.rsplit("/", 2)[-2]}'


print('\nInfoBoard Pi configuration script')
print('================================= \n')

SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
ROOT_FOLDER = os.path.realpath(os.path.join(SCRIPT_FOLDER, '..', '..'))
CFG_FILE = os.path.join(ROOT_FOLDER, 'config.yaml')
DATA_CFG_FILE = os.path.join(ROOT_FOLDER, 'data', 'config.yaml')
if not os.path.isfile(CFG_FILE):
    print('Installation configuration file config.yaml doesn\'t found, '
          'place config.yaml in the root of repository folder.')
    exit()

with open(CFG_FILE, 'r') as cfg_file:
    cfg = yaml.safe_load(cfg_file)


default_media_dir = cfg.get('default_media_dir')

if default_media_dir is None:
    default_media_dir = os.path.join(ROOT_FOLDER, 'data')
    print(f'Media default directory doesn\'t found in the config.yaml, fallback to the default {default_media_dir}')

if cfg.get('auto_mount') == True:
    all_block_devices = set(linux_block_devices())
    used_block_devices = set((p.device for p in psutil.disk_partitions()))
    unused_block_devices = all_block_devices - used_block_devices
    available = [device for device in unused_block_devices if device.startswith('/dev/sd')]

    if not available:
        print('Automount set, but the available drive is not detected, '
              'insert the usb drive and make sure it is not mounted.')
        exit()
    print('Automount set, select the device for automount:\n')

    while True:
        for idx, a_device in enumerate(available):
            print(f'[{idx}] {a_device}')

        s_device = input('Choose the device for automount: ')
        try:
            s_device = int(s_device)
            if s_device < 0 or s_device >= len(available):
                raise ValueError()

        except ValueError:
            print(f'\nIncorrect input, write number in range 0-{len(available) - 1}, or Ctrl+Z for exit')
            continue

        automount_device = available[s_device]
        break

    while True:
        s_path = input(f'Choose the folder for mounting, (default: {default_media_dir}): ')
        print(s_path)
        if not s_path:
            s_path = default_media_dir
        try:
            pathlib.Path(s_path).mkdir(parents=True, exist_ok=True)
        except ValueError:
            print(f'\nIncorrect directory, try it again or Ctrl+Z for exit')
            continue
        print(s_path)
        os.chmod(s_path, 0o777)
        automount_path = s_path
        print(automount_path)
        break

if cfg.get('auto_mount') == True:
    print(f'Automount set, mounting {automount_device} to {automount_path}...')
    mount = sh.Command('mount')
    mount(automount_device, automount_path)

    with open(f'{ROOT_FOLDER}/automount.sh', "w") as f:
        f.write(f"#!/bin/bash\n\nsudo mount {automount_device} {automount_path}\nchmod -R 755 {automount_path}")
else:
    with open(f'{ROOT_FOLDER}/automount.sh', "w") as f:
        f.write(f"#!/bin/bash")

auto_power_off = cfg.get('auto_power_off')
if auto_power_off is not None:
    apo_time = auto_power_off.split(':')
    failed = True
    if len(apo_time) == 2:
        try:
            apo_hours = int(apo_time[0])
            apo_minutes = int(apo_time[1])
        except ValueError:
            pass
        else:
            if apo_hours >= 0 and apo_hours < 24 and apo_minutes >= 0 and apo_minutes < 60:
                failed = False

    if failed:
        print('Auto power off format is wrong it should be HH:MM')
        exit()

if not os.path.isfile(DATA_CFG_FILE):
    print('Data configuration file doesn\'t exist, creating new one based on template')

    if not os.path.isdir(os.path.dirname(DATA_CFG_FILE)):
        print(f'Directory {os.path.dirname(DATA_CFG_FILE)} does not exist, creating it')
        os.makedirs((os.path.dirname(DATA_CFG_FILE)))

    cfg_template = {'default_slide_time': 60,
                    'auto_update': cfg.get('auto_update_data_config', True),
                    'default_media_dir': os.path.realpath(default_media_dir),
                    'media': [{'url': '', 'slide_time': 60}],
                    'server': {'cookie': {'expiry_days': 1,
                                          'key': str(uuid.uuid4()),
                                          'name': 'infoboard-pi'},
                               'credentials': {'usernames': {'admin': {'failed_login_attempts': 0,
                                                                       'name': 'Administrator',
                                                                       'password': '$2b$12$oQuBEF8QQO3HNnhqiqGoVuTzr4zyvv20khfsKCQmWVePRrRvErA2a'},
                                                             }
                                               }
                               }
                    }
    with open(DATA_CFG_FILE, 'w') as cfg_file:
        yaml.dump(cfg_template, cfg_file)
else:
    with open(DATA_CFG_FILE, 'r') as cfg_file:
        cfg_data = yaml.safe_load(cfg_file)
    updated = False
    if 'auto_update_data_config' in cfg.keys():
        cfg_data['auto_update'] = cfg.get('auto_update_data_config')
        updated = True
    if 'default_slide_time' in cfg.keys():
        cfg_data['default_slide_time'] = cfg.get('default_slide_time')
        updated = False
    cfg_data['default_media_dir'] = os.path.realpath(default_media_dir)
    if updated:
        print('Updating data config file ...')
        with open(DATA_CFG_FILE, 'w') as cfg_file:
            yaml.dump(cfg_data, cfg_file)


print('Setting cron jobs ...')
cron = CronTab(user='root')
cron.remove_all(comment='infoboard-pi')
job = cron.new(command=f'/bin/bash {ROOT_FOLDER}/src/scripts/checker.sh > /var/log/infoboard.log 2>&1', comment='infoboard-pi')
job.minute.every(1)
job = cron.new(command=f'/bin/bash {ROOT_FOLDER}/src/scripts/check_server.sh > /var/log/infoboard.log 2>&1', comment='infoboard-pi')
job.minute.every(1)
if auto_power_off is not None:
    job = cron.new(command=f'poweroff',
                   comment='infoboard-pi')
    job.hour.on(apo_hours)
    job.minute.on(apo_minutes)

cron.write()





