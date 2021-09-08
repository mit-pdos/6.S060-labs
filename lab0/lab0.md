# 6.S060 Lab 0

In this lab you will get acquainted with the photo-sharing codebase, allowing users to add information to their public profile.

## Scenario

The scenario for this lab is straightforward.  Alice, a user of our photo-sharing application, would like to post public information about herself, such as her personal website or email address.

Right now our public profiles are very bare-bones.  We'd like to let her add these personal attributes to her profile.

There are no security features in this lab.  Its main purpose is to get your feet wet with the codebase.  Let us know if you have any issues.

## More specifically

Implement a feature which allows Alice's client to update a dictionary of personal user attributes, in addition to querying other users' attributes.

### Your job

is to implement `update_public_profile_infos` and `get_friend_public_profile` in `client.py` to allow Alice to change this field.

You will not be able to modify any other files given to you.

Hints that may be useful to you:
 - `api.PublicProfile.infos` is a dictionary which consists of keys---attribute names for the user---and values---the corresponding attribute values.
 - You can ask the server to `update_public_profile` of Alice by passing in an `api.UpdatePublicProfileRequest` with the appropriate `api.PublicProfile` object.
 - You can run the autograder on your assignment by running `make lab0-ag`.

### To submit lab 0

upload a ZIP file containing `client.py` to [Gradescope](https://www.gradescope.com/courses/281655/assignments/1473448).
