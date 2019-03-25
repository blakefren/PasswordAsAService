"""
This script performs unit testing for PasswordAsAService web API.
It is intended to run with the included /etc/passwd and /etc/group files.

This does not read the passwd and group files to check the data, it only
validates that the data was returned in the correct format, edge cases, etc.
"""

import sys
import os
from flask import Flask, request
import unittest
import json
from itertools import combinations
from service import app

# Adjust these to test with other user/group.
dummy_user = 0
dummy_group = 0
user_cols = ['name', 'uid', 'gid', 'comment', 'home', 'shell']
group_cols = ['name', 'gid', 'member']
group_cols_output = ['name', 'gid', 'members']


class TestService(unittest.TestCase):

    def test_users_all(self):
        # Test all users status code.

        self.test_app = app.test_client()
        response = self.test_app.get('/users')
        self.assertEqual(response.status_code, 200)

        '''with app.test_client() as client:  # Testing query URL.
            response = client.get('/users')
            print(request.url)
            print(response.status_code)'''

    def test_users_all_data(self):
        # Check all users data.

        self.test_app = app.test_client()
        response = self.test_app.get('/users')

        json_vals = self.valid_json(response.data)

        # JSON return is invalid.
        if json_vals is None:
            self.assertTrue(False)

        # Test the valid JSON.
        else:

            # Make sure we have users.
            self.assertTrue(len(json_vals) > 0)

            # Check for all user columns in returned data.
            self.valid_user_data(json_vals, False)

    def test_users_single(self):
        # Test single user status code.

        self.test_app = app.test_client()
        response = self.test_app.get('/users/' + str(dummy_user))  # dummy user.
        self.assertEqual(response.status_code, 200)

        response = self.test_app.get('/users/1000000')  # non-existent user.
        self.assertEqual(response.status_code, 404)

        response = self.test_app.get('/users/asdf')  # non-integer uid.
        self.assertEqual(response.status_code, 404)

    def test_users_single_data(self):
        # Test single user data.

        self.test_app = app.test_client()
        response = self.test_app.get('/users/' + str(dummy_user))  # dummy group.

        json_vals = self.valid_json(response.data)

        # JSON return is invalid.
        if json_vals is None:
            self.assertTrue(False)

        # Test the valid JSON.
        else:

            # Make sure we have a user.
            self.assertTrue(len(json_vals) > 1)

            # Check for all user columns in returned data.
            self.valid_user_data(json_vals, True)

    def test_users_query(self):
        # Test users query status code.

        self.test_app = app.test_client()
        dummy_dict = {
            'name': '',
            'uid': 1000000,
            'gid': 1000000,
            'comment': '',
            'home': '',
            'shell': ''
        }

        # Get all combinations of querystring args.
        combos = []
        for i in range(len(user_cols)+1):
            for item in combinations(user_cols, i):
                temp = {}
                for param in list(item):
                    temp[param] = dummy_dict[param]
                combos.append(temp)

        # Iterate through all combinations of querystring args.
        for item in combos:
            response = self.test_app.get('/users/query', query_string=item)
            self.assertEqual(response.status_code, 200)

        # Run query with non-supported arg.
        response = self.test_app.get('/users/query', query_string={'asdf': 'fdsa'})
        self.assertEqual(response.status_code, 200)

    def test_users_query_data(self):
        # Test users query data.

        self.test_app = app.test_client()
        dummy_dict = {
            'name': 'root',
            'uid': 0,
            'gid': 0,
            'comment': 'System Operator',
            'home': '/',
            'shell': '/bin/ksh'
        }

        # Get all combinations of querystring args.
        combos = []
        for i in range(len(user_cols) + 1):
            for item in combinations(user_cols, i):
                temp = {}
                for param in list(item):
                    temp[param] = dummy_dict[param]
                combos.append(temp)

        # Iterate through all combinations of querystring args.
        for item in combos:
            response = self.test_app.get('/users/query', query_string=item)

            # Test for valid JSON.
            json_vals = self.valid_json(response.data)

            # JSON return is invalid.
            if json_vals is None:
                self.assertTrue(False)

            # Test the valid JSON.
            else:

                # No need to validate if we have a user.
                # Some queries may not return any users.

                # Check for all user columns in returned data.
                self.valid_user_data(json_vals, False)

        # Run query with non-supported arg.
        response = self.test_app.get('/users/query', query_string={'asdf': 'fdsa'})
        json_vals = self.valid_json(response.data)
        if json_vals is None:
            self.assertTrue(False)
        else:

            # No need to validate if we have a user.
            # Some queries may not return any users.

            # Check for all user columns in returned data.
            self.valid_user_data(json_vals, False)

    def test_users_groups(self):
        # Test user group status code.

        self.test_app = app.test_client()
        response = self.test_app.get('/users/' + str(dummy_user) + '/groups')  # dummy user.
        self.assertEqual(response.status_code, 200)

        response = self.test_app.get('/users/1000000/groups')  # non-existent user.
        self.assertEqual(response.status_code, 404)

        response = self.test_app.get('/users/asdf/groups')  # non-integer uid.
        self.assertEqual(response.status_code, 404)

    def test_users_groups_data(self):
        # Test user group data.

        self.test_app = app.test_client()
        response = self.test_app.get('/users/' + str(dummy_user) + '/groups')  # dummy user.

        json_vals = self.valid_json(response.data)

        # JSON return is invalid.
        if json_vals is None:
            self.assertTrue(False)

        # Test the valid JSON.
        else:

            # No need to validate if we have a group.
            # Some users may not be in any groups.

            # Check for all group columns in returned data.
            self.valid_group_data(json_vals, False)

    def test_groups_all(self):
        # Test all groups status code.

        self.test_app = app.test_client()
        response = self.test_app.get('/groups')
        self.assertEqual(response.status_code, 200)

    def test_groups_all_data(self):
        # Check all groups data.

        self.test_app = app.test_client()
        response = self.test_app.get('/groups')

        json_vals = self.valid_json(response.data)

        # JSON return is invalid.
        if json_vals is None:
            self.assertTrue(False)

        # Test the valid JSON.
        else:

            # Make sure we have groups.
            self.assertTrue(len(json_vals) > 0)

            # Check for all group columns in returned data.
            self.valid_group_data(json_vals, False)

    def test_groups_single(self):
        # Test single group status code.

        self.test_app = app.test_client()
        response = self.test_app.get('/groups/' + str(dummy_group))  # dummy group.
        self.assertEqual(response.status_code, 200)

        response = self.test_app.get('/groups/1000000')  # non-existent group.
        self.assertEqual(response.status_code, 404)

        response = self.test_app.get('/groups/asdf')  # non-integer gid.
        self.assertEqual(response.status_code, 404)

    def test_groups_single_data(self):
        # Test single group data.

        self.test_app = app.test_client()
        response = self.test_app.get('/groups/' + str(dummy_group))  # dummy group.

        json_vals = self.valid_json(response.data)

        # JSON return is invalid.
        if json_vals is None:
            self.assertTrue(False)

        # Test the valid JSON.
        else:

            # Make sure we have a group.
            self.assertTrue(len(json_vals) > 1)

            # Check for all group columns in returned data.
            self.valid_group_data(json_vals, True)

    def test_groups_query(self):
        # Test groups query status code.

        self.test_app = app.test_client()
        dummy_dict = {
            'name': '',
            'gid': 1000000,
            'member': ''
        }

        # Get all combinations of querystring args.
        combos = []
        for i in range(len(group_cols) + 1):
            for item in combinations(group_cols, i):
                temp = {}
                for param in list(item):
                    temp[param] = dummy_dict[param]
                combos.append(temp)

        # Iterate through all combinations of querystring args.
        for item in combos:
            response = self.test_app.get('/groups/query', query_string=item)
            self.assertEqual(response.status_code, 200)

        # Run query with non-supported arg.
        response = self.test_app.get('/groups/query', query_string={'asdf': 'fdsa'})
        self.assertEqual(response.status_code, 200)

    def test_groups_query_data(self):
        # Test groups query data.

        self.test_app = app.test_client()
        dummy_dict = {
            'name': 'bin',
            'gid': 2,
            'member': ['root', 'daemon']
        }

        # Get all combinations of querystring args.
        combos = []
        for i in range(len(group_cols) + 1):
            for item in combinations(group_cols, i):
                for j in range(1, len(dummy_dict['member'])+1):  # Adding to get all member combos.
                    for jtem in combinations(dummy_dict['member'], j):  # Adding to get all member combos.
                        temp = {}
                        for param in list(item):
                            if param == 'member':
                                temp[param] = list(jtem)
                            else:
                                temp[param] = dummy_dict[param]
                        if temp not in combos:
                            combos.append(temp)

        # Iterate through all combinations of querystring args.
        for item in combos:
            response = self.test_app.get('/groups/query', query_string=item)

            # Test for valid JSON.
            json_vals = self.valid_json(response.data)

            # JSON return is invalid.
            if json_vals is None:
                self.assertTrue(False)

            # Test the valid JSON.
            else:

                # No need to validate if we have a group.
                # Some queries may not return any groups.

                # Check for all groups columns in returned data.
                self.valid_group_data(json_vals, False)

        # Run query with non-supported arg.
        response = self.test_app.get('/groups/query', query_string={'name': 'root', 'asdf': 'fdsa'})
        json_vals = self.valid_json(response.data)
        if json_vals is None:
            self.assertTrue(False)
        else:

            # No need to validate if we have a group.
            # Some queries may not return any groups.

            # Check for all groups columns in returned data.
            self.valid_group_data(json_vals, False)

    # Methods below are called by testing methods above.

    def valid_json(self, data):
        # Tests for valid json.

        valid_json_flag = False
        json_vals = None
        try:
            json_vals = json.loads(data)
            valid_json_flag = True
        except ValueError:
            pass
        self.assertTrue(valid_json_flag)

        return json_vals

    def valid_user_data(self, data, single_user):
        # Checks user data.

        if single_user:
            self.assertEqual(list(data.keys()), user_cols)
        else:
            for user in data:
                self.assertEqual(list(user.keys()), user_cols)

    def valid_group_data(self, data, single_group):
        # Checks group data.

        if single_group:
            self.assertEqual(list(data.keys()), group_cols_output)
        else:
            for group in data:
                self.assertEqual(list(group.keys()), group_cols_output)
