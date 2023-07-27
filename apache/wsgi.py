activate_this = "/var/www/sl1cer/venv/bin/activate_this.py"
exec(open(activate_this).read())
import sys

sys.path.insert(0, "/var/www/sl1cer/")
from app import	app as application
