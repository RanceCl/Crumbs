from app import create_app

app = create_app(config_name="default")

if __name__ == '__main__':
    from app.models import *
    #from app.routes import *
    app.run(debug=True)
