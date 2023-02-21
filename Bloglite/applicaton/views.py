from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like, Follower
import requests
from . import db


views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    # Get the IDs of users that the current user is following
    following_ids = []
    for follower in current_user.following:
        following_ids.append(follower.user_id)
    # Get the posts created by users that the current user is following
    following_posts = Post.query.filter(Post.author.in_(following_ids)).all()
    # Get the current user's posts
    user_posts = current_user.posts
    # Combine the two lists of posts
    posts = following_posts + user_posts
    return render_template("home.html", user=current_user, posts=posts)


@login_required
@views.route("/create-post", methods=['GET', 'POST'])
def create_post():
    # Check if request method is POST
    if request.method == "POST":
        # Get text from request form
        text = request.form.get('text')

        # Check if text is empty
        if not text:
            flash("Post cannot be empty", category="error")
        else:
            # Create new post object with text and current user's ID
            post = Post(text=text, author=current_user.id)
            # Add post to database session
            db.session.add(post)
            # Commit changes to the database
            db.session.commit()
            # Flash success message
            flash("Post created!", category='success')
            # Redirect to home page
            return redirect(url_for('views.home'))

    # Render the create_post template
    return render_template("create_post.html", user=current_user, User=User)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    # Get post with specified id
    post = Post.query.filter_by(id=id).first()

    # Check if post exists
    if not post:
        flash("Post does not exist", category='error')
    else:
        # Delete post from the database
        db.session.delete(post)
        # Commit changes to the database
        db.session.commit()
        flash('Post deleted', category="success")

    # Redirect to home page
    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def post(username):
    # Get the user with the specified username
    user = User.query.filter_by(username=username).first()
    # Check if the user exists
    if not user:
        flash("No with that username exist", category="error")
        redirect(url_for('views.home'))
    # Get all posts by the user
    posts = user.posts

    user_id = user.id

    # Check if the current user is following the user
    following = Follower.query.filter_by(
        user_id=user.id, follower_id=current_user.id).first()

    # Render the posts template and pass the current user, posts, username, User, following, and user_id
    return render_template("posts.html", user=current_user, posts=posts, username=username, User=User, following=following, user_id=user_id)


@views.route("/create-comment/<post_id>", methods=["POST"])
@login_required
def create_comment(post_id):
    # Get text from request form
    text = request.form.get('text')

    # Check if text is empty
    if not text:
        flash("Comment can not be empty", category="error")
    else:
        # Get the post with the specified id
        post = Post.query.filter_by(id=post_id).first()
        # Check if post exists
        if post:
            # Create new comment object with text, current user's ID, and post_id
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            # Add comment to database session
            db.session.add(comment)
            # Commit changes to the database
            db.session.commit()
        else:
            flash("Post does not exist", category="error")

    # Redirect to home page
    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    # Get the comment with the specified id
    comment = Comment.query.filter_by(id=comment_id).first()

    # Check if the comment exists
    if not comment:
        flash('Comment does not exist.', category='error')
    # Check if the current user is the author of the comment or the post
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        # Delete the comment from the database
        db.session.delete(comment)
        # Commit changes to the database
        db.session.commit()

    # Redirect to the home page
    return redirect(url_for('views.home'))


@views.route("/like-post/<post_id>", methods=["GET"])
@login_required
def like(post_id):
    # Get the post with the specified id
    post = Post.query.filter_by(id=post_id).first()
    # Get the like by the current user on the post
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()
    # Check if the post exists
    if not post:
        flash('Post does not exist', category='error')
    # Check if the current user has already liked the post
    elif like:
        # Unlike the post
        db.session.delete(like)
        db.session.commit()
    else:
        # Create a new like
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    # Redirect to the home page
    return redirect(url_for('views.home'))


@views.route("/follow_unfollow/<username>", methods=["POST"])
@login_required
def follow_unfollow(username):
    # Get the user to follow/unfollow
    user_to_follow = User.query.filter_by(username=username).first()

    # Check if the user exist
    if not user_to_follow:
        flash("User does not exist", category="error")
        return redirect(url_for("views.home"))
    # check if user try to follow himself
    if user_to_follow.id == current_user.id:
        flash("You cannot follow yourself", category="error")
        return redirect(url_for("views.home"))

    # Check if the current user is already following the user
    following = Follower.query.filter_by(
        user_id=user_to_follow.id, follower_id=current_user.id).first()

    try:
        if following:
            # If the current user is already following the user, unfollow them
            db.session.delete(following)
            db.session.commit()
            flash(
                f"You have unfollowed {user_to_follow.username}", category="success")
        else:
            # If the current user is not already following the user, follow them
            follow = Follower(user_id=user_to_follow.id,
                              follower_id=current_user.id)
            db.session.add(follow)
            db.session.commit()
            flash(
                f"You are now following {user_to_follow.username}", category="success")
    except Exception as e:
        flash("An error occurred while following the user", category="error")
        # You may want to log the exception for debugging purposes
        raise e
    return redirect(url_for('views.post', username=username))


@views.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        # Get the search query from the form
        query = request.form.get("query")

        # Search for users with a username that contains the query
        users = User.query.filter(User.username.like(f"%{query}%")).all()

        return render_template("search.html", user=current_user, users=users)
    else:
        # Render the search template when accessed via GET request
        return render_template("search.html", user=current_user)



@views.route("/edit/<id>", methods=['GET', 'POST'])
@login_required
def edit(id):
    # Get the post with the given ID
    post = Post.query.get(id)

    # Check if the post exists and if the current user is the author
    if not post or current_user.id != post.author:
        flash("Post does not exist or you do not have permission to edit it",
              category="error")
        return redirect(url_for('views.home'))

    # If the request method is GET, render the edit form
    if request.method == "GET":
        return render_template("edit.html", user=current_user, post=post)

    # If the request method is POST, update the post with the new data
    if request.method == "POST":
        text = request.form.get('text')
        if not text:
            flash("Post cannot be empty", category="error")
        else:
            post.text = text
            db.session.commit()
            flash("Post updated!", category='success')
            return redirect(url_for('views.home'))


@views.route('/user_engagement/<int:user_id>')
def user_engagement(user_id):
    # Retrieve the user engagement data from the API
    user_engagement = requests.get(
        f'http://localhost:5000/api/user_engagement/{user_id}').json()
    nested_dict = user_engagement['user_engagement']
    # Render the user engagement template and pass the data to it
    return render_template('user_engagement.html', user_engagement=nested_dict, user=current_user)
