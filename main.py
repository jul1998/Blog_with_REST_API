from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField, CKEditorField
from datetime import date



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()
##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

all_posts_query = db.session.query(BlogPost).all()


@app.route('/')
def get_all_posts():
    posts = [post for post in all_posts_query]
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = BlogPost.query.get(index)
    print(requested_post.title)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/new-post", methods=["GET","POST"])
def create_post():
    form = CreatePostForm()
    isEditPost =False
    if form.validate_on_submit():
        today = date.today()
        title_data = form.title.data
        subtitle_data = form.subtitle.data
        author_data = form.author.data
        img_url_data = form.img_url.data
        body_data = form.body.data
        new_post = BlogPost(title=title_data,
                            date=today.strftime("%B %d, %Y"),
                            subtitle=subtitle_data,
                            author=author_data,
                            img_url=img_url_data,
                            body=body_data)
        db.session.add(new_post)
        db.session.commit()
        print("Success")
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html",isEditPost=isEditPost, form=form)

@app.route("/edit-post/<int:post_id>", methods=["GET","POST"])
def edit_post(post_id):
    isEditPost = True
    requested_post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        img_url=requested_post.img_url,
        author=requested_post.author,
        body=requested_post.body
    )

    if edit_form.validate_on_submit():
        requested_post.title = edit_form.title.data
        requested_post.subtitle = edit_form.subtitle.data
        requested_post.author = edit_form.author.data
        requested_post.img_url = edit_form.img_url.data
        requested_post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", index=post_id))

    return render_template("make-post.html", isEditPost=isEditPost, form=edit_form)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)