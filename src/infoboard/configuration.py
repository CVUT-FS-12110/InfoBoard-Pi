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


print('\nInfoBoard Pi configuration script')
print('================================= \n')

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

if cfg.get('auto_mount') == True:
    if os.path.commonpath([data_cfg_file, ROOT_FOLDER]) == ROOT_FOLDER:
        print('\nauto_mount is set to true, data configuration file has to be pointed outside of the infoboard reopository')
        exit()

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
        s_path = input(f'Choose the folder for mounting, (default: {os.path.dirname(data_cfg_file)}: ')
        if not s_path:
            s_path = os.path.dirname(data_cfg_file)
        try:
            pathlib.Path(s_path).mkdir(parents=True, exist_ok=True)
        except ValueError:
            print(f'\nIncorrect directory, try it again or Ctrl+Z for exit')
            continue
        os.chmod(s_path, 0o777)
        automount_path = s_path
        break

if cfg.get('auto_mount') == True:
    print(f'Automount set, mounting {automount_device} to {automount_path}...')
    mount = sh.Command('mount')
    mount(automount_device, automount_path)

    with open(f'{ROOT_FOLDER}/automount.sh', "w") as f:
        f.write(f"#!/bin/bash\n\nsudo mount {automount_device} {automount_path}")
else:
    with open(f'{ROOT_FOLDER}/automount.sh', "w") as f:
        f.write(f"#!/bin/bash")

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
                    'default_media_dir': os.path.join(ROOT_FOLDER, 'data'),
                    'media': [{'url': '', 'slide_time': 60}]
                    }
    with open(data_cfg_file, 'w') as cfg_file:
        yaml.dump(cfg_template, cfg_file)

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





