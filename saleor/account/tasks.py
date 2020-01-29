import logging
import os
import shlex
import subprocess

from django.conf import settings

from ..celeryconf import app

logger = logging.getLogger(__name__)


def run_shell_command(command_line):
    """ accept shell command and run"""
    command_line_args = shlex.split(command_line)
    logger.info('Subprocess: "' + ' '.join(command_line_args) + '"')

    work_dir = os.path.abspath(os.path.join(settings.MEDIA_ROOT, '..'))

    try:
        command_line_process = subprocess.Popen(
            command_line_args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=work_dir
        )

        command_line_process.communicate()
        command_line_process.wait()
    except (OSError, subprocess.CalledProcessError) as exception:
        logger.info('Exception occured: ' + str(exception))
        logger.info('Subprocess failed')
        return False
    else:
        # no exception was raised
        logger.info('Subprocess finished')
    return True


@app.task
def guetzli_compress_image(image_path):
    # create guetzli link under /usr/local/bin
    GUETZLI_CMD = '/usr/local/bin/guetzli'
    logger.info('guetzli_compress_image: image_path=%s' % image_path)

    if os.path.exists(GUETZLI_CMD):
        cmd = '%s --quality 84 %s %s' % (GUETZLI_CMD, image_path, image_path)
        run_shell_command(cmd)
