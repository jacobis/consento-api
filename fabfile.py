# encoding: utf-8

'''
Created on Aug 26, 2014

@author: Jacob Sungwoon Lee
'''

from fabric import colors
from fabric.contrib.console import confirm
from fabric.api import abort, cd, env, local, run, prefix, settings, sudo, task


########## GLOBALS

env.roledefs = {
    'app': ['54.183.205.145:22'],
}
env.user = 'ubuntu'
env.run = 'python manage.py'

DEFAULT_PORT = 8000
DEFAULT_DJANGO_SETTINGS_MODULE = 'consento.settings.dev'

SERVER_WORKON_HOME = '/home/ubuntu/VirtualEnvs'
SERVER_PROJECT_HOME = '/home/ubuntu/VirtualEnvs/consento-api/consento-project'
SERVER_PROJECT_REQ_HOME = SERVER_PROJECT_HOME + '/reqs'
SERVER_DJANGO_SETTINGS_MODULE = 'consento.settings.prod'

ACTIVATE = 'source %s/consento-api/bin/activate' % SERVER_WORKON_HOME

########## END GLOBALS


########## SERVERS

@task
def app():
    env.setdefault('django_settings_module', '--settings=%s' % SERVER_DJANGO_SETTINGS_MODULE)
    env.roles = ['app']
    env.key_filename = '/home/jacob/Dropbox/Development/Keys/dmis_key.pem'

########## END SERVERS


########## DEFAULT COMMANDS

@task
def runserver(port=DEFAULT_PORT, settings=DEFAULT_DJANGO_SETTINGS_MODULE):
    """
    Runserver running with Werkzeug debugger.
    """
    local('%s runserver_plus 0.0.0.0:%s --settings=%s' % (env.run, port, settings))


@task
def shell(settings=DEFAULT_DJANGO_SETTINGS_MODULE):
    """
    Run Django shell with autoloading of the apps database models.
    """
    local('%s shell_plus --settings=%s' % (env.run, settings))

########## END DEFAULT COMMANDS


########## GUNICORN MANAGEMENT

@task
def restart_gunicorn():
    """
    Restart the gunicorn process.
    """
    print(colors.magenta('======> ' + colors.cyan('Restart gunicorn servers.')))
    if sudo('supervisorctl restart all', quiet=True).succeeded:
        print(colors.green('Gunicorn restart is Succeeded.'))
    else:
        print(colors.red('Gunicorn restart is Failed.'))

########## END GUNICORN


########## SERVER MANAGEMENT

@task
def deploy():
    """
    Deploy to server automatically.
    """
    if not confirm('Now, deploy to the %s automatically, continue anyway?' % env.host):
        abort('Aborting at user request.')
    
    with cd(SERVER_PROJECT_HOME):
        print(colors.magenta('======> ' + colors.cyan('Update source code from github.')))
        run('git stash save', quiet=True)
        run('git pull origin master')

        with prefix(ACTIVATE):
            with cd(SERVER_PROJECT_REQ_HOME):
                print(colors.magenta('======> ' + colors.cyan('Install requirement modules.')))
                run('pip install -r prod.txt')

            print(colors.magenta('======> ' + colors.cyan('Start collectstatic.')))
            run('%s collectstatic --noinput --settings=%s' % (env.run, SERVER_DJANGO_SETTINGS_MODULE))

    restart_gunicorn()

########## END SERVER MANAGEMENT
