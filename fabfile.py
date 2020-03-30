from fabric.api import env, prefix, run, task
from fabric.context_managers import cd, shell_env
from fabric.contrib.files import exists

env.forward_agent = True
env.colorize_errors = True

env.hosts = ["smallweb1.ebmdatalab.net"]
env.user = "root"
env.path = "/var/www/opencodelists"


def initalise_directory():
    if not exists(env.path):
        run(
            "git clone git@github.com:ebmdatalab/opencodelists.git {}".format(
                env.path
            )
        )


def create_venv():
    if not exists("venv"):
        run("python3.5 -m venv venv")


def update_from_git():
    run("git fetch --all")
    run("git checkout --force origin/master")


def install_requirements():
    with prefix("source venv/bin/activate"):
        run("pip install -r requirements.txt")


def chown_everything():
    run("chown -R www-data:www-data {}".format(env.path))


def run_migrations():
    with prefix("source venv/bin/activate"):
        run("python manage.py migrate")


def set_up_systemd():
    run(
        "ln -sf {}/deploy/systemd/app.opencodelists.web.service /etc/systemd/system".format(
            env.path
        )
    )

    run("systemctl daemon-reload")


def restart_service():
    run("systemctl restart app.opencodelists.web.service")


@task
def deploy():
    initalise_directory()

    with cd(env.path):
        with shell_env(DJANGO_SETTINGS_MODULE="opencodelists.settings"):
            create_venv()
            update_from_git()
            install_requirements()
            run_migrations()
            chown_everything()
            set_up_systemd()
            restart_service()
