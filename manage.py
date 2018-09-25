"""
前提，安装了flask_migrate，flask_script
数据库迁移，命令：
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
"""

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app.models.base import db
from fisher import app

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()