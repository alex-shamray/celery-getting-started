from proj.tasks import add

"""
*Canvas*: Designing Work-flows
==============================

You just learned how to call a task using the tasks ``delay`` method,
and this is often all you need, but sometimes you may want to pass the
signature of a task invocation to another process or as an argument to another
function, for this Celery uses something called *signatures*.

A signature wraps the arguments and execution options of a single task
invocation in a way such that it can be passed to functions or even serialized
and sent across the wire.

You can create a signature for the ``add`` task using the arguments ``(2, 2)``,
and a countdown of 10 seconds like this:
"""

print(add.signature((2, 2), countdown=10))
# tasks.add(2, 2)

"""
There's also a shortcut using star arguments:
"""

print(add.s(2, 2))
# tasks.add(2, 2)

"""
And there's that calling API again…
-----------------------------------

Signature instances also supports the calling API: meaning they
have the ``delay`` and ``apply_async`` methods.

But there's a difference in that the signature may already have
an argument signature specified. The ``add`` task takes two arguments,
so a signature specifying two arguments would make a complete signature:
"""

s1 = add.s(2, 2)
res = s1.delay()
print(res.get())
# 4

"""
But, you can also make incomplete signatures to create what we call
*partials*:
"""

# incomplete partial: add(?, 2)
s2 = add.s(2)

"""
``s2`` is now a partial signature that needs another argument to be complete,
and this can be resolved when calling the signature:
"""

# resolves the partial: add(8, 2)
res = s2.delay(8)
print(res.get())
# 10

"""
Here you added the argument 8 that was prepended to the existing argument 2
forming a complete signature of ``add(8, 2)``.

Keyword arguments can also be added later, these are then merged with any
existing keyword arguments, but with new arguments taking precedence:
"""

s3 = add.s(2, 2, debug=True)
# s3.delay(debug=False)   # debug is now False.

"""
As stated signatures supports the calling API: meaning that;

- ``sig.apply_async(args=(), kwargs={}, **options)``

    Calls the signature with optional partial arguments and partial
    keyword arguments. Also supports partial execution options.

- ``sig.delay(*args, **kwargs)``

  Star argument version of ``apply_async``. Any arguments will be prepended
  to the arguments in the signature, and keyword arguments is merged with any
  existing keys.

So this all seems very useful, but what can you actually do with these?
To get to that I must introduce the canvas primitives…

The Primitives
--------------

.. topic:: \

    .. hlist::
        :columns: 2

        - :ref:`group <canvas-group>`
        - :ref:`chain <canvas-chain>`
        - :ref:`chord <canvas-chord>`
        - :ref:`map <canvas-map>`
        - :ref:`starmap <canvas-map>`
        - :ref:`chunks <canvas-chunks>`

These primitives are signature objects themselves, so they can be combined
in any number of ways to compose complex work-flows.

.. note::

    These examples retrieve results, so to try them out you need
    to configure a result backend. The example project
    above already does that (see the backend argument to :class:`~celery.Celery`).

Let's look at some examples:

Groups
~~~~~~

A :class:`~celery.group` calls a list of tasks in parallel,
and it returns a special result instance that lets you inspect the results
as a group, and retrieve the return values in order.
"""

from celery import group
from proj.tasks import add

print(group(add.s(i, i) for i in range(10))().get())
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

"""
- Partial group
"""

g = group(add.s(i) for i in range(10))
print(g(10).get())
# [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

"""
Chains
~~~~~~

Tasks can be linked together so that after one task returns the other
is called:
"""

from celery import chain
from proj.tasks import add, mul

# (4 + 4) * 8
print(chain(add.s(4, 4) | mul.s(8))().get())
# 64

"""
or a partial chain:
"""

# (? + 4) * 8
g = chain(add.s(4) | mul.s(8))
print(g(4).get())
# 64

"""
Chains can also be written like this:
"""

print((add.s(4, 4) | mul.s(8))().get())
# 64

"""
Chords
~~~~~~

A chord is a group with a callback:
"""

from celery import chord
from proj.tasks import add, xsum

print(chord((add.s(i, i) for i in range(10)), xsum.s())().get())
# 90

"""
A group chained to another task will be automatically converted
to a chord:
"""

print((group(add.s(i, i) for i in range(10)) | xsum.s())().get())
# 90

"""
Since these primitives are all of the signature type they
can be combined almost however you want, for example:
"""

# upload_document.s(file) | group(apply_filter.s() for filter in filters)

"""
Be sure to read more about work-flows in the :ref:`Canvas <guide-canvas>` user
guide.
"""
