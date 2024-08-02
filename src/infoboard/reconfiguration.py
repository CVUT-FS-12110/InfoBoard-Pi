import os
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


print('\nInfoBoard Pi reconfiguration script')
print('===================================== \n')
print('If you want reconfigure automount, starts uninstall.sh and then install.sh again')

SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
ROOT_FOLDER = os.path.realpath(os.path.join(SCRIPT_FOLDER, '..', '..'))
CFG_FILE = os.path.join(ROOT_FOLDER, 'config.yaml')
if not os.path.isfile(CFG_FILE):
    print('Installation configuration file config.yaml doesn\'t found, '
          'place config.yaml in the root of repository folder.')
    exit()

with open(CFG_FILE, 'r') as cfg_file:
    cfg = yaml.safe_load(cfg_file)


data_cfg_file = cfg.get('configuration_file')

if data_cfg_file is None:
    print('Data configuration file url doesn\'t found in the config.yaml, fallback to the default url ./data')
    data_cfg_file = os.path.join(ROOT_FOLDER, 'data', 'configuration.yaml')


data_cfg_file = os.path.abspath(data_cfg_file)

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

if not os.path.isfile(data_cfg_file):
    print('Data configuration file doesn\'t exist, creating new one based on template')

    if not os.path.isdir(os.path.dirname(data_cfg_file)):
        print(f'Directory {os.path.dirname(data_cfg_file)} does not exist, creating it')
        os.makedirs((os.path.dirname(data_cfg_file)))

    cfg_template = {'default_slide_time': 60,
                    'auto_update': cfg.get('auto_update_data_config', True),
                    'default_media_dir':  os.path.realpath(os.path.dirname(data_cfg_file)),
                    'media': [{'url': '', 'slide_time': 60}]
                    }
    with open(data_cfg_file, 'w') as cfg_file:
        yaml.dump(cfg_template, cfg_file)
else:
    with open(data_cfg_file, 'r') as cfg_file:
        cfg_data = yaml.safe_load(cfg_file)
    updated = False
    if 'auto_update_data_config' in cfg.keys():
        cfg_data['auto_update'] = cfg.get('auto_update_data_config')
        updated = True
    if 'default_slide_time' in cfg.keys():
        cfg_data['default_slide_time'] = cfg.get('default_slide_time')
        updated = False
    if updated:
        print('Updating data config file ...')
        with open(data_cfg_file, 'w') as cfg_file:
            yaml.dump(cfg_data, cfg_file)


print('Setting cron jobs ...')
cron = CronTab(user='root')
cron.remove_all(comment='infoboard-pi')
job = cron.new(command=f'/bin/bash {ROOT_FOLDER}/src/scripts/checker.sh > /var/log/infoboard.log 2>&1', comment='infoboard-pi')
job.minute.every(1)
if auto_power_off is not None:
    job = cron.new(command=f'poweroff',
                   comment='infoboard-pi')
    job.hour.on(apo_hours)
    job.minute.on(apo_minutes)

cron.write()





