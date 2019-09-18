from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .models import Votes, Likes


def save_user_vote(request, object):
    """
    It looks for "vote" named button in POST method
    I've made it that way so people can't send link to their
    exercise with automated upvote or downvote.

    Using  Generic Relations and unique_together this short code
    create an upvote or downvote, and catches IntegrityError in case
    where someone has voted already before. It allows me to avoid situation
    someone upvotes and downvotes at the same time, or gives more upvotes or
    downvotes than he should.


    object: it should be a variable with object we want to upvote/downvote
    """
    if request.POST['vote'] == 'upvote':
        try:
            object.votes.create(activity_type=Votes.UP_VOTE, user=request.user)
        except IntegrityError:
            obj = object.votes.get(user=request.user)
            obj.activity_type = Votes.UP_VOTE
            obj.save()
    else:
        try:
            object.votes.create(activity_type=Votes.DOWN_VOTE, user=request.user)
        except IntegrityError:
            obj = object.votes.get(user=request.user)
            obj.activity_type = Votes.DOWN_VOTE
            obj.save()


def user_vote(request, object):
    """
    Checks activity of specific user to specific task
    """
    # votes = object.votes.filter(user=request.user)
    # return {vote.get_activity_type_display(): True for vote in votes}
    try:
        return object.votes.get(user=request.user).get_activity_type_display()
    except ObjectDoesNotExist:
        return None


def user_likes(request, object):
    """
    Checks activity of specific user to specific task
    """
    likes = []
    for comment in object.comments.all():
        try:
            likes.append(comment.likes.get(user=request.user).comment.id)
        except ObjectDoesNotExist:
            pass
    return likes