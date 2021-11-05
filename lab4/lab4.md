# 6.S060 Lab 4

In this lab you will manage code from an untrusted source.

## Scenario

Alice, who has been adding photos to her application, realizes that she would like to do things with them before sharing them with the world.  In particular, she would like to organize her photos
```
$ image-recognize photo-taken-oct-31.jpg
adorable scottish terrier
```
and edit them
```
$ social-media-filter --input=mediocre-lockdown-pastry.jpg --output=professional-baker-macaron.jpg
```

The programs Alice would like to run on her data are fairly complex, and she can't write them herself.  Instead, she downloads them from strangers on the Web.
```
$ wget https://definitely-legitimate-site.mit.edu.example.com/file?name=image-recognize
$ image-recognize photo-taken-oct-31.jpg
...
```
One issue with this approach is that the programs she downloads are difficult for her to audit.  In particular, they may be fairly complex, and moreover, their sources may be unavailable.  If the program authors are malicious or incompetent, or someone is able to replace the programs with bad programs, these programs may be able to read her private photos or tamper with her public ones.  Can we prevent this?

As covered in lecture, we can place the untrusted code Alice would like to run in a _sandbox_.  In particular, we will use sandbox [WebAssembly](https://en.wikipedia.org/wiki/WebAssembly) code to isolate the trusted Python host code of the photo application from the untrusted binaries which read and write Alice's images.

To control the binaries' access to Alice's image database, Alice's client will enforce a basic security policy.  In particular, each of Alice's photos may be associated with a set of _tags_ which are short strings grouping the photos.  Whenever her client executes an untrusted program, it will do so with a tag which determines the set of photos it has access to.  Additionally, a photo may be designated as _read-only_, which prevents any program from modifying it.

## More specifically

Alice's client must be able to safely execute programs, which are arbitrary WebAssembly binaries, on her photos.

We deal with a specific, simple photo format.  (You can assume that photos in more complicated formats have already been safely decoded to this one.)  In particular, a photo is represented by a width _W_ and a height _H_, both of which are 32-bit integers, as well as a vector of 32-bit integers specifying three color channels plus an alpha channel.  The size of the vector is _WH_, and it consists of the concatentation of each row of the image, starting from the top.

To define our security goal, we will assign each photo a unique identifier, called a _photo ID_.  In addition to the photo data itself, which consists of a width, a height, and a vector of bytes, each photo ID will be mapped to two pieces of information: a bit indicating whether the photo is read-only, and a set of strings called the photo's _tags_.

When an untrusted program executes, it creates an _instance_ of itself which runs with permissions corresponding to a specific tag.  This program can enumerate the photos which it has access to, query their width and height dimensions, and request its host to read a photo into sandbox memory or save a photo in sandbox memory on the host.  Our goals thus correspond to the following desired properties.  (You should know what's coming by now...)

  1. **Correctness**.  If the program were written correctly, and it is given a security policy that accommodates the photo IDs it would like to read and write with, then the client should execute the program correctly (as if there were no sandbox).
  2. **Security**.  Different instances of programs should be isolated from each other and the host system.  In particular:

     - No instance of a program may be able to read or write photo data mapped by any ID not tagged with the tag it is running with.
     - No program may be able to write photo data mapped by any ID which is read-only.
     - No program should be able to interfere with or crash the host system or the execution of any other program.

You may assume that tags are fixed and the read only bit is constant while a program is executing.

### Your job

is to modify the code in `photobox.py` to correctly and safely sandbox untrusted code.

As with the previous labs, _this is an open-ended assignment!_  Again, you may modify any code in `photobox.py` so long as you do not change the signatures of the public members of the file (i.e., `__init__` methods or methods not beginning with an underscore `_`).  However, your sandbox must still be usable by the host photo application, you will **not** be able to modify any other files given to you.

Hints that may be useful to you:

 - Our threat model is quite different from those in prior labs (local software instead of a remote server), so you may need some time to get acquainted with the new codebase.  Start early!
   - Type annotations have been added to make it easier to consume the new code.
 - You may find it useful to read the [`wasmer` WebAssembly API documentation](https://wasmerio.github.io/wasmer-python/api/wasmer/index.html) to understand how embedding WebAssembly binaries works.
 - You will not need to modify any C source code to complete the assignment.  However, to figure out how to achieve correctness, you might find it useful to read through the sample image filters.  In particular, `host.h` defines the interface the C code is expecting from the Python host.
 - Unlike in some other implementations, an exception in a callback provided to the binary will not have its traceback propagated through the call stack.  We have provided a `wrap_finally` helper function to print these out.

### To submit lab 4

upload a ZIP file containing `photobox.py` to [Gradescope](https://www.gradescope.com/courses/281655).
