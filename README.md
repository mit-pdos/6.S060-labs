# 6.S060 Labs

This git repository contains the code for the labs in 6.S060.

In these labs, you will add a series of security features to a photo-sharing application.

## Dependencies

These labs depend on Python 3.9.  You can verify that your Python version is correct by checking
```
$ python3 --version
3.9.x
```
where "x" is any number.

## Tests

To run tests for these lab, run `make test`, which will run Python [doctests](https://docs.python.org/3/library/doctest.html).  They should all pass.

Note that these tests are different from the tests used by the autograder, which will be used to grade your assignments.

## Web app

The photo-sharing application supports a (very rudimentary) web application interface written in [Flask](https://flask.palletsprojects.com/en/2.0.x/).  To use the interface, run `make web`.

## Assignments

You can find all the code required for each lab inside of its directory.  For instance, the code for [lab0](lab0/) resides in `lab0/`.

You can find the tasks for the corresponding assignment by looking at the Markdown file associated with the lab number.  The following files contain descriptions of the tasks for each lab:

 - [lab0](lab0/lab0.md)
 - [lab1](lab1/lab1.md)
 - [lab2](lab2/lab2.md)
 - [lab3](lab3/lab3.md)
 - [lab4](lab4/lab4.md)
 - [lab5](lab5/lab5.md)

## Contributions

We'd be happy to accept any contributions.  Feel free to issue a PR on [GitHub](https://github.com/mit-pdos/6.S060-labs/compare) and we'll take a look.  If we merge it, let us know if you'd like attribution.
