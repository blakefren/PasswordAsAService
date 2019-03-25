# Project Title

This is a python web API. It is intended to be used in a Unix-like system to expose the information contained in the /etc/passwd and /etc/group files.

## Getting Started

You can also follow the [Flask - getting started](http://flask.pocoo.org/docs/1.0/quickstart/) documentation for general Flask setup info.

### Prerequisites

In addition to Python 3.6 or newer, you'll need the following packages:

```
flask
nose (for unit testing)
```

### Installing

Download the git repo or the zip file, and save to a directory on your system. 
NOTE: the service will exit with HTTP code 500 if the /etc/passwd and /etc/group files are not present in either the user-specified location (below) or the default Unix location.

To run, you can either:
* double-click the service.py file (will run in debug mode), or
* input "python -O service.py" in a terminal window in the project directory, or
* perform the following in a terminal window in the project directory:
    * Unix:
        * $ export FLASK_APP=service.py
        * $ flask run
    * Windows (powershell):
        * PS C:\path\to\app> $env:FLASK_APP = "service.py"
        * PS C:\path\to\app> flask run

You can run a sample test by sending a HTTP GET request to localhost:5000/users to return a list of all users in the /etc/passwd file. If you're running windows, you'll have to either:
* copy the included /etc/ folder to C:\etc\, or 
* modify service.py to look in the included /etc/ directory by modifying (examples included):
    * global variable user_path
    * global variable group_path

## Running the tests

test_all.py contains all unit tests. The unit tests do the following:
* Test each API method to ensure the expected HTTP return code.
* Query each API method to check that the output is valid JSON.
* Query each API method to check that the output has the correct data outputs.

It does NOT check the service data against the file data. Test cases for that can be added if desired.

To run unit tests, open a terminal window and navigate to the service directory. After installing nose, run the following command:

```
nosetests
```

If you want to run the service in debug mode, just follow the [Flask instructions](http://flask.pocoo.org/docs/1.0/quickstart/#debug-mode) if you're running the service via the "flask run" option. Alternatively, in the command-line option, run it without the "-O" flag ("python service.py"). Double-clicking the file will always run in debug mode.

### API queries supported:

```
localhost:5000/users - returns list of all users in system
localhost:5000/users/query - returns list of users matching any querystring arguments (name/uid/gid/comment/home/shell)
localhost:5000/users/1234 - returns user with uid "1234"
localhost:5000/users/1234/groups - returns list of groups that user with uid "1234" is a member of
localhost:5000/groups - returns list of all groups in system
localhost:5000/groups/query - returns list of groups matching any querystring arguments (name/gid/member) (any number of members)
localhost:5000/groups/4321 - returns group with gid "4321"
```

## Deployment

As the [Flask documentation](http://flask.pocoo.org/docs/1.0/deploying/#deployment) says, it's not really built for production. In fact, please don't, because this service is just a toy and is not the type of thing to actually use. If you're really stuck on it, just follow instructions in the Flask documentation link above.

## Built With

* [Flask](http://flask.pocoo.org/) - The web framework.
* [nose](https://nose.readthedocs.io/) - Used to perform unit testing.

## Authors

* **Blake French**

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
