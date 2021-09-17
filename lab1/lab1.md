# 6.S060 Lab 1

In this lab you will design and implement a secure client synchronization protocol.

## Scenario

Consider the following setup.  Alice has two devices: a laptop and a mobile phone.  Both of these devices communicate with our server, which hosts our photo-sharing application.
```
Alice's laptop          <------>
                                  Server
Alice's mobile phone    <------>
```

One feature we may wish to support is to allow Alice's laptop to synchronize its photos with her phone.  In particular, let's say that Alice posts a photo from her laptop.

```
                         tim.jpg
Alice's laptop           ------>
                                  Server
Alice's mobile phone     ------
```

Later, she logs onto the application from her phone and downloads the photo for viewing.  Unfortunately, with the current code in `client.py`, the server is able to surreptitiously replace this photo with a different one.

```
Alice's laptop           ------
                                  Server
Alice's mobile phone    <------
                      crimson.jpg
```

How can we help Alice avoid this attack?  As covered in lecture, we will be using message authentication codes to prevent the malicious server from tampering with the photos.

Whenever one of Alice's devices modifies her data on the server (e.g., when they `Client.register` with the server or they `Client.put_photo` onto it), it will also create an authenticated log entry to be stored by that server.

Later, when another of Alice's devices connects to the server, it may invoke `Client._synchronize`.  The client will in turn request logs from the server via a remote `Server.synchronize` call.  The server will respond with the authenticated logs which Alice allegedly posted.

Because her devices share a secret unknown to the server, Alice's devices will be able to detect if the server has tampered with any of the logs, which were authenticated with that secret.  In particular, if the log has not been tampered with, Alice's device should apply the operation associated with that log.  If the device does detect evidence of foul play, however, it should raise a `errors.SynchronizationError`, which indicates that it was unable to synchronize correctly.

## More specifically

We assume that all of Alice's devices are able to share a secret out-of-band---perhaps via a passphrase, over a separately authenticated channel.

Suppose Alice has two devices: the `old_device` and the `new_device`.

Suppose moreover that `old_device` issues a series of updates to the server, where the first update registers Alice with the server, and subsequent updates add her photos to the server.

Alice now logs into the server with `new_device`.  Alice calls `new_device.list_photos` and `new_device.get_photo` to view her pictures on her new device.

A secure implementation of client synchronization guarantees the following, even with a malicious server:

 - `new_device.list_photos()` returns a prefix of the photo IDs in `old_device.list_photos()`.
   - Moreover, if the server was actually operating properly, `new_device.list_photos() == old_device.list_photos()`.  (This is a _correctness_ requirement.)
 - For every photo ID `id` inside the list returned by `new_device.list_photos()`, `new_device.get_photo(id) == old_device.get_photo(id)`.
 - If the client detects malicious behavior on the part of the server during synchronization, it must raise a `errors.SynchronizationError`.

### Your job

is to add authentication to the `Client` in the `client` module, so that Alice's new device will be able to guarantee the properties above, despite the machinations of the corrupt server.

_This is an open-ended assignment!_  In contrast to lab 0, you will be designing your own authentication protocol.  There are many different ways to solve this problem.  It may take a few iterations to converge to a good design.  We recommend you to start design work early.

You may modify any code in `client.py` so long as you do not change the signatures of the public methods of `Client` (i.e., the `__init__` method or methods not beginning with an underscore `_`).  However, since your `Client` must still talk to our server, you will **not** be able to modify any other files given to you.

Hints that may be useful to you:

 - You may find it helpful to maintain separate notes or a design document as you program to clarify your approach.  (At least one TA finds that writing out a protocol forces him to think unambiguously about the problem.)
 - One common problem is producing a secure _but incorrect_ synchronization implementation which rejects good log entries (when the server is not misbehaving).  **It may help to run `make test` to debug these kinds of problems.**
 - The `crypto` module contains routines for creating message authentication codes and hashes of lists of data, given a `crypto.UserSecret`.
 - In addition to the cryptographic operations, `api.PutPhotoRequest` and `api.RegisterRequest` both require objects of type `codec.Encoding`, which is a class to help you transform a sequence of Python `int` and `bytes` objects into a single `bytes` object.
 - You can turn a `str` object `x` into a `bytes` object with the method `x.encode('utf-8')`.
 - There is some helper code in `client.py` which may help you as you build your solution, such as the `LogEntry` class or the `_record_new_photo` method.  They may help you to structure your solution.  You may find it useful to modify these.
 - We've provided a server which handles requests correctly.  Our autograder's server will not be as cooperative...
   - If you have issues with failing tests, you may find it helpful to inspect and alter the autograder source to assist you in the debugging process.  The autograder lives in the `ag1` subdirectory.

### To submit lab 1

upload a ZIP file containing `client.py` to [Gradescope](https://www.gradescope.com/courses/281655).
