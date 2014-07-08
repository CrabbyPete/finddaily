from os.path                 import dirname,abspath,join
from fabric.api              import *
from fabric.context_managers import prefix
from contextlib              import contextmanager


env.project_dir    = dirname( dirname( abspath(__file__) ) )
env.code_dir       = join(env.project_dir,'finddaily/')
env.activate       = '. bin/activate'
env.hosts          = ['localhost']
env.use_ssh_config = True
env.show = ['debug']

@contextmanager
def virtualenv():
    with cd( env.project_dir ):
        with prefix(env.activate):
            yield

def deploy():
    local( "git pull" )
    with virtualenv():

        with cd( env.code_dir ):
            run( "pip install -r requirements.txt" )
            result = run('ls')
            print result
            result = run( "python ./test.py" )
            if result.fail:
               print "Test failed"

