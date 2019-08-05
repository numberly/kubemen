from kubemen.app import app

if __name__ == "__main__":
    config = app.config.get_namespace("APP_", lowercase=True)
    app.run(**config)
