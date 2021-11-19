# 6.S060 Lab 5

In this lab you will mount your own attack to extract a secret token from a "VeRY Secur3 SerVer".

## Scenario

The scenario of this lab is simple.
You are now the attacker.

Bob is trying to save his favorite cryptocoin $ecret key on a server so he can easily verify if he is remembering it correctly.
To do this, Bob sends a request containing his key on a secure connection to the server.
The server replies with a bit that indicates whether the secret in the request matches the one on the server.

Even though the server does not authenticate the party making the request, Bob believes that he is safe as the API is very restricted: an attacker trying to guess the secret by querying the API learns no information other than whether it was correct.

Prove him wrong!

## More specifically

On initialization, a `SecureServer` instance generates a secret token using fresh randomness and saves it as a hexadecimal string i.e., one with characters from `0` to `9` or `a` to `f`. Note that you need **two** hexadecimal characters to represent one byte of data.

The `SecureServer` allows any user to submit a `VerifyTokenRequest` with some token.
The server responds with a `VerifyTokenResponse`, which contains a single boolean value.
This value is `True` if the token in the request matches the server's secret.
Otherwise, the value is `False`.

In addition to this correctness property, Bob claims that the server has the following security property: there is a negligible probability that an attacker can recover the secret token from the server in polynomial time (with respect to the length of the token).

Unfortunately, implementation errors make it possible for you, the attacker, to violate this property.
In particular, software side channels (specifically, timing side channels) foil Bob's attempt to achieve this property.

### Your job
is to implement `steal_secret_token` in `attacker.py` to steal the secret token from the server.

Unlike in previous labs, timing side channels have nondeterministic behavior.
Thus, while we have provided an autograder to help you develop your solution locally, **you will need it to submit it to our [autograder on Gradescope](https://www.gradescope.com/courses/281655) to receive an accurate evaluation.**

In particular,
 - The autograder will test whether you can extract secret tokens of different lengths.  The length **in bytes** is the `l` parameter to `steal_secret_token`.
 - Every test will wait 20 minutes for the attacker to extract the secret token.  Your attack must complete by this time (or the autograder will reject it).
 - Your attack must not crash or fail (or the autograder will reject it).
 - To compute your final grade, the autograder will only be run a limited number of times per student.  Make sure that your attack succeeds with a comfortably-high probability.

Finaly, note that you are expected to respect the python conventions and you should not simply access private variables when not allowed.

For the rest, have fun and good luck!

### To submit lab 5

leave your ZIP file containing `attacker.py` on [Gradescope](https://www.gradescope.com/courses/281655).
