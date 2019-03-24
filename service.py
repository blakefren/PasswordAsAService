"""
This module is a web API that returns information related to UNIX /etc/passwd and /etc/group files.
It uses Flask and returns the data in JSON format.
"""


from flask import Flask, request, abort
from json import dumps
import csv
import os
import copy


# Set global user variables.
last_user_time = None
user_list = []
user_path = None  # os.path.join(os.getcwd(), 'etc', 'passwd')  # Change to supply non-default passwd file path.
user_path_default = os.path.join(os.sep, 'etc', 'passwd')
user_cols = ['name', 'uid', 'gid', 'comment', 'home', 'shell']

# Set global group variables.
last_group_time = None
group_list = []
group_path = None  # os.path.join(os.getcwd(), 'etc', 'group', 'TEST')  # Change to supply non-default group file path.
group_path_default = os.path.join(os.sep, 'etc', 'group')
group_cols = ['name', 'gid', 'members']

# Initiate the service.
app = Flask(__name__)


@app.route('/users', methods=['GET'])
def get_users_all():
    """Return a list of all users."""

    # Get all users, convert to JSON.
    all_users = []
    for user in read_users():
        temp_json = {}
        for j in range(len(user_cols)):
            temp_json[user_cols[j]] = convert_to_int(user[j])
        all_users.append(temp_json)

    return dumps(all_users)


@app.route('/users/query', methods=['GET'])
def get_users_query():
    """Return list of users matching search criteria (exact match)."""

    # These items will default to None if not present in querystring.
    name = request.args.get('name')
    uid = request.args.get('uid')
    gid = request.args.get('gid')
    comment = request.args.get('comment')
    home = request.args.get('home')
    shell = request.args.get('shell')
    in_args = [name, uid, gid, comment, home, shell]

    # Get users that match criteria.
    sorted_users = copy.deepcopy(read_users())
    remove_list = []
    for i, user in enumerate(sorted_users):

        # Check all search criteria for each user.
        remove_user = False
        for j in range(len(user_cols)):
            if in_args[j] is not None and in_args[j] != user[j]:
                remove_user = True
                break

        # If no match, add to list for removal.
        if remove_user:
            remove_list.append(i)

        # If match, convert to JSON.
        else:
            temp_json = {}
            for j in range(len(user_cols)):
                temp_json[user_cols[j]] = convert_to_int(user[j])
            sorted_users[i] = temp_json

    # Remove users with no match.
    for index in sorted(remove_list, reverse=True):
        del sorted_users[index]

    return dumps(sorted_users)


@app.route('/users/<int:uid>', methods=['GET'])
def get_user_single(uid):
    """Return single user matching uid."""

    # Filter to single user.
    found_user = None
    for user in read_users():
        if user[user_cols.index('uid')] == str(uid):
            found_user = user
            break
    if found_user is None:
        abort(404)

    # Convert user to JSON.
    return_json = {}
    for i in range(len(user_cols)):
        return_json[user_cols[i]] = convert_to_int(found_user[i])

    return dumps(return_json)


@app.route('/users/<int:uid>/groups', methods=['GET'])
def get_user_groups(uid):
    """Return all groups that user is a member of."""

    # Get user name from uid.
    name = None
    for user in read_users():
        if user[user_cols.index('uid')] == str(uid):
            name = user[user_cols.index('name')]
            break
    if name is None:
        abort(404)

    # Filter to list of groups.
    return_groups = []
    for group in read_groups():
        if name in group[group_cols.index('members')]:
            temp_json = {}
            for j in range(len(group_cols)):
                temp_json[group_cols[j]] = convert_to_int(group[j])
            return_groups.append(temp_json)

    return dumps(return_groups)


@app.route('/groups', methods=['GET'])
def get_groups_all():
    """Return list of all groups."""

    # Get all groups, convert to JSON.
    all_groups = []
    for group in read_groups():
        temp_json = {}
        for j in range(len(group_cols)):
            temp_json[group_cols[j]] = convert_to_int(group[j])
        all_groups.append(temp_json)

    return dumps(all_groups)


@app.route('/groups/query', methods=['GET'])
def get_groups_query():
    """Return list of groups matching search criteria (exact match)."""

    # These items will default to None if not present in querystring.
    name = request.args.get('name')
    gid = request.args.get('gid')
    member = request.args.getlist('member')
    if len(member) == 0 or member is None:
        member = []
    in_args = [name, gid, member]

    # Get groups that match criteria.
    sorted_groups = copy.deepcopy(read_groups())
    remove_list = []
    for i, group in enumerate(sorted_groups):

        # Check all search criteria for each group.
        remove_group = False
        for j in range(len(group_cols)):

            # For name and gid.
            if j != 2:
                if in_args[j] is not None and in_args[j] != group[j]:
                    remove_group = True
                    break

            # Check all members; if any are missing, remove.
            elif j == 2:
                for member in in_args[2]:
                    if member not in group[2]:
                        remove_group = True
                        break

        # If no match, add to list for removal.
        if remove_group:
            remove_list.append(i)

        # If match, convert to JSON.
        else:
            temp_json = {}
            for j in range(len(group_cols)):
                temp_json[group_cols[j]] = convert_to_int(group[j])
            sorted_groups[i] = temp_json

    # Remove groups with no match.
    for index in sorted(remove_list, reverse=True):
        del sorted_groups[index]

    return dumps(sorted_groups)


@app.route('/groups/<int:gid>', methods=['GET'])
def get_group_single(gid):
    """Return single group matching gid."""

    # Filter to single group.
    found_group = None
    for group in read_groups():
        if group[group_cols.index('gid')] == str(gid):
            found_group = group
            break

    if found_group is None:
        abort(404)

    # Convert group to JSON.
    return_json = {}
    for i in range(len(group_cols)):
        return_json[group_cols[i]] = convert_to_int(found_group[i])
    return_json = dumps(return_json)

    return return_json


@app.after_request
def apply_headers(response):
    """Tell receiving app that data is JSON via response header."""

    response.headers['content-type'] = 'application/json'
    return response


def read_users():
    """
    Check last user file modify time.
    If different than stored time, read the file.
    Return user info.
    """

    global last_user_time
    global user_list

    # Check last file modification time.
    file_name = None
    file_mod_time = None
    try:
        file_mod_time = os.path.getmtime(user_path)
        file_name = user_path
    except (OSError, TypeError):
        print('\n\tError accessing provided user file.')
        print('\tDefaulting to standard user file\n.')
        try:
            file_mod_time = os.path.getmtime(user_path_default)
            file_name = user_path_default
        except OSError:
            abort(500)
    if last_user_time == file_mod_time and user_list != []:
        return user_list

    # Read user file, store info as list of lists.
    user_list = []
    last_user_time = file_mod_time
    try:
        with open(file_name, 'r', newline='') as passwd:
            reader = csv.reader(passwd, delimiter=':')
            for row in reader:
                row.pop(1)  # Remove password field.
                if len(row) != len(user_cols):
                    raise IndexError
                user_list.append(row)
    except (OSError, IndexError):
        abort(500)

    return user_list


def read_groups():
    """
    Check last group file modify time.
    If different than stored time, read the file.
    Return group info.
    """

    global last_group_time
    global group_list

    # Check last file modification time.
    file_name = None
    file_mod_time = None
    try:
        file_mod_time = os.path.getmtime(group_path)
        file_name = group_path
    except (OSError, TypeError):
        print('\n\tError accessing provided group file.')
        print('\tDefaulting to standard group file.\n')
        try:
            file_mod_time = os.path.getmtime(group_path_default)
            file_name = group_path_default
        except OSError:
            abort(500)
    if last_group_time == file_mod_time and group_list != []:
        return group_list

    # Read group file, store info as list of lists.
    group_list = []
    last_group_time = file_mod_time
    try:
        with open(file_name, 'r', newline='') as group:
            reader = csv.reader(group, delimiter=':')
            for row in reader:
                row.pop(1)  # Remove password field.
                if len(row) != len(group_cols):
                    raise IndexError
                row[-1] = row[-1].split(',')  # Split member field from CSV to list.
                row[-1] = [item.replace(' ', '') for item in row[-1]]  # Trim whitespace.
                if len(row[-1]) == 1 and '' in row[-1]:
                    row[-1] = []  # Handle empty list case.
                group_list.append(row)
    except (OSError, IndexError):
        abort(500)

    return group_list


def convert_to_int(s):
    """Convert any object to int if possible, otherwise return original object."""

    try:
        return int(s)
    except (ValueError, TypeError):
        return s


if __name__ == '__main__':
    if __debug__:
        app.run(debug=True)
    else:
        app.run()
