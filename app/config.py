from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager


app = Flask(__name__, static_folder="static", template_folder="templates")
mail = Mail(app) # this instantiates the mail class

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# mail config
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "<yourmail>@gmail.com"
app.config['MAIL_PASSWORD'] = "<your app password key from google>"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


login = LoginManager()
login.init_app(app)
login.login_view = "sign_in" # execute to that route function if user is not signed in


app.secret_key = "96BC1618F9B9263F8214DB9C9C4EE"
db.create_all()