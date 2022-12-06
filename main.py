from flask import Flask, render_template, redirect, url_for,flash,abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy 
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from forms import CreatePostForm , RegistrationForm , LoginForm , CommentForm
from werkzeug.security import check_password_hash , generate_password_hash
from flask_login import UserMixin , login_user , LoginManager , login_required , current_user , logout_user
from functools import wraps
from flask_gravatar import Gravatar




app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##Flask login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "You Need To Login "

##gravatar
gravatar = Gravatar(app, size=20, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


##CONFIGURE TABLE

class User(UserMixin,db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    # users can have many posts
    posts = db.relationship('BlogPost' , backref='poster')
    
    #users can comment on posts
    comments = db.relationship('Comments' , backref='user_comment')

    
class BlogPost(UserMixin,db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    # foreign key to link user (refer to the primary key of User)
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    # author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # one blog can have many comments
    comments = db.relationship('Comments', backref='blog_comment')

class Comments(UserMixin,db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer , primary_key=True)
    # foreign key to link users
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    #foreign key to link blogpost
    blog_id = db.Column(db.Integer,db.ForeignKey('blog_posts.id'))
    text = db.Column(db.Text , nullable=False)
    



with app.app_context():
    db.create_all()

## Here is our Decorators Function Which Allows only admin to create,edit,delete posts
def admin_only(f):
    @wraps(f)
    def decorator_function(*args,**kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.is_authenticated:
            if current_user.id != 1:
                return abort(403)
            #other continue with route function
            return f(*args,**kwargs)
    return decorator_function
    

@app.route('/register',methods=['POST','GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        salted_hashed_password = generate_password_hash(
            password=form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email = form.email.data,
            password = salted_hashed_password,
            name = form.name.data
        )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html",form=form,logged_in=current_user.is_authenticated,user=current_user)


@app.route('/login',methods = ['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user:
            flash(message="Email Not found please register")
        elif not check_password_hash(user.password , form.password.data):
            flash("Please Check your Password")
        else:
            login_user(user)
            return redirect(url_for("get_all_posts"))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated , user=current_user)


@app.route('/logout')   
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))


   

@app.route('/')
def get_all_posts():
    with app.app_context():
        posts = db.session.query(BlogPost).all()

    return render_template("index.html", allposts=posts,logged_in=current_user.is_authenticated , user=current_user)


@app.route("/post/<id>",methods=['GET','POST'])
def show_post(id):
    form = CommentForm()
    requested_post = BlogPost.query.filter_by(id=id).first()
    if form.validate_on_submit():
        commenter = current_user.id
        new_comment=Comments(
            user_id=commenter,
            blog_id = id,
            text = form.comment.data
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post,logged_in=current_user.is_authenticated , user=current_user,
                           form=form)



@app.route("/about")
def about():
    return render_template("about.html",logged_in=current_user.is_authenticated , user=current_user)


@app.route("/contact")
def contact():
    return render_template("contact.html",logged_in=current_user.is_authenticated , user=current_user)

@app.route("/Create-post",methods=['GET','POST'])
@admin_only
def create_post():
    form = CreatePostForm()
    poster = current_user.id
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author_id=poster,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html",form=form,logged_in=current_user.is_authenticated , user=current_user)

@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    poster = current_user.id
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body

    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        author_id = poster
        post.body = edit_form.body.data
        post.img_url = edit_form.img_url.data
        post.subtitle = edit_form.subtitle.data
        db.session.commit()
        return redirect(url_for("show_post", id=post.id))


    return render_template("make-post.html", form=edit_form, is_edit=True ,logged_in=current_user.is_authenticated , user=current_user)

@app.route("/delete/<id>")
@admin_only
def delete_blog(id):
    post_to_delete = BlogPost.query.filter_by(id=id).first()
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

if __name__ == "__main__":
    app.run(debug=True)

