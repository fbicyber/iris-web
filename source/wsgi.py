import os

from app import create_app
from app.extensions import db


app = create_app()

app.logger.warning("===============================")
app.logger.warning(f"| IRIS IS READY on port  {os.getenv('INTERFACE_HTTPS_PORT')} |")
app.logger.warning("===============================")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

