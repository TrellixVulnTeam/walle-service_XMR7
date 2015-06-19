from cloudify import ctx
import fabric


def _run(command):
    ctx.logger.info(command)
    out = fabric.api.run(command)
    ctx.logger.info(out)


def install(config):
    ctx.logger.info("Config: " + str(config))
    _run("""
sudo apt-get update 2>&1
sudo apt-get install -y postgresql postgresql-contrib 2>&1
    """)
