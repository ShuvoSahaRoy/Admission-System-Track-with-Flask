from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from main_app import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def get_reset_token(self,expires_sec=120):
        s= Serializer(app.secret_key,expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.secret_key)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"


class Departments(db.Model):
    department_name = db.Column(db.String(80), primary_key=True, nullable=False)
    total_seat = db.Column(db.Integer, nullable=False)
    stu_dept = db.relationship('Students', backref='student', lazy=True)

    def __repr__(self):
        return f"Departments('{self.department_name}','{self.total_seat}')"


class Students(db.Model):
    admission_num = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(15), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    department = db.Column(db.String(80), db.ForeignKey('departments.department_name'), nullable=False)

    def __repr__(self):
        return f"Students('{self.name}','{self.department}')"
