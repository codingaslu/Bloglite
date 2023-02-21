from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from . import db # Import the database object from the current package
from .models import User, Post, Comment, Like, Follower # Import the models


api = Api()

class UserEngagement(Resource):
    def get(self, user_id):
        # Retrieve the user with the specified ID
        user = User.query.filter_by(id=user_id).first()
        
        if user:
            
            # Get the user's name
            user_name= user.username
            
            # Get the user's posts, comments, and likes
            posts = user.posts
            comments = user.comments
            likes = user.likes

            # Calculate the total number of comments and likes for the user
            total_comments = len(comments)
            total_likes = len(likes)

            # Calculate the total number of followers and followed users for the user
            total_followers = user.followers.count()
            total_following = user.following.count()

            # Create a dictionary to store the user engagement data
            user_engagement = {
                'username': user_name,
                'user_id': user_id,
                'total_posts': len(posts),
                'total_comments': total_comments,
                'total_likes': total_likes,
                'total_followers': total_followers,
                'total_following': total_following
            }

            return {'user_engagement': user_engagement}
        else:
            # Return an error if the user is not found
            return {'error': 'User not found.'}, 404

api.add_resource(UserEngagement, '/api/user_engagement/<int:user_id>')

