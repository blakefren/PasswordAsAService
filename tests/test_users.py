"""
This script performs unit testing for PasswordAsAService web API.
"""


import pytest


base_url = 'localhost:5000/'


############## Test each of the web API methods from service.py. ##############

# /users
# Return all users.


# /users/query
# Return users who match query parameters.
# Querystring can include: name, uid, gid, comment, home, and shell.


# /users/<int:uid>
# Returns single user matching uid.


# /users/<int:uid>/groups
# Returns groups that user (uid) is a member of.


# /groups
# Returns all groups.


# /groups/query
# Returns groups that match query parameters.
# Querystring can include: name, gid, and any number of members.


# /groups/<int:gid>
# Returns single group matching gid.


