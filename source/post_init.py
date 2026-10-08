from app import create_app

app = create_app()

with app.app_context():
    from app.post_init import run_post_init
    run_post_init(development=app.config["DEVELOPMENT"])
