import os
import yaml
from crontab import CronTab
import psutil
import glob
import pathlib

def linux_block_devices():
    for blockdev_stat in glob.glob('/sys/block/*/stat'):
        blockdev_dir = blockdev_stat.rsplit('/', 1)[0]
        found_parts = False
        for part_stat in glob.glob(blockdev_dir + '/*/stat'):
            yield blockdev_stat.rsplit('/', 2)[-2]
            found_parts = True
        if not found_parts:
            yield blockdev_dir.rsplit('/', 1)[-1]

print('InfoBoard Pi uninstall script')
print('============================= \n')

SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
ROOT_FOLDER = os.path.realpath(os.path.join(SCRIPT_FOLDER, '..', '..'))

print('Removing cron entries ...')

cron = CronTab(user='root')
cron.remove_all(comment='infoboard-pi')
cron.write()

print('Removing automount script ...')
try:
    os.remove(f'{ROOT_FOLDER}/automount.sh')
except OSError:
    pass





