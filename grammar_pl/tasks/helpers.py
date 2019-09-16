from django.db import IntegrityError
from .models import Activity


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
    if 'vote' in request.POST:
        if request.POST['vote'] == 'upvote':
            try:
                object.votes.create(activity_type=Activity.UP_VOTE, user=request.user)
            except IntegrityError:
                object.votes.get(user=request.user).delete()
                object.votes.create(activity_type=Activity.UP_VOTE, user=request.user)
        else:
            try:
                object.votes.create(activity_type=Activity.DOWN_VOTE, user=request.user)
            except IntegrityError:
                object.votes.get(user=request.user).delete()
                object.votes.create(activity_type=Activity.DOWN_VOTE, user=request.user)


def get_votes(object):
    """
    It gets a number of upvotes, and downvotes of specific object
    Then it returns is as a dictionary dict['upvote'] = number_of_upvotes
    """
    votes = dict(upvotes=object.votes.filter(activity_type=Activity.UP_VOTE).count(),
                 downvotes=object.votes.filter(activity_type=Activity.DOWN_VOTE).count())
    return votes


def user_activity(request, object):
    """
    Checks activity of specific user to specific task
    """
    activities = object.votes.filter(user=request.user)
    dictionary = dict()
    for activity in activities:
        dictionary[activity.get_activity_type_display()] = True
    return dictionary
