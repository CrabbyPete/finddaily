from fabric.api              import *
from fabric.context_managers import prefix
from contextlib              import contextmanager



env.project_dir    = '/home/pete/finddaily'
env.code_dir       = '/home/pete/finddaily/finddaily/'
env.activate       = 'source ./bin/activate'
env.hosts          = ['localhost']
env.use_ssh_config = True

@contextmanager
def virtualenv():
    with cd( env.project_dir ):
        with prefix(env.activate):
            yield

def deploy():
    local( "git pull" )
    with virtualenv():
        with cd( env.code_dir ):
            result = run( "python test.py" )

