import traceback

from proj.tasks import add

"""
Calling Tasks
=============

You can call a task using the :meth:`delay` method:
"""

add.delay(2, 2)

"""
This method is actually a star-argument shortcut to another method called
:meth:`apply_async`:
"""

add.apply_async((2, 2))

"""
The latter enables you to specify execution options like the time to run
(countdown), the queue it should be sent to, and so on:
"""

add.apply_async((2, 2), queue='lopri', countdown=10)

"""
In the above example the task will be sent to a queue named ``lopri`` and the
task will execute, at the earliest, 10 seconds after the message was sent.

Applying the task directly will execute the task in the current process,
so that no message is sent:
"""

print(add(2, 2))
# 4

"""
These three methods - :meth:`delay`, :meth:`apply_async`, and applying
(``__call__``), represents the Celery calling API, that's also used for
signatures.

A more detailed overview of the Calling API can be found in the
:ref:`Calling User Guide <guide-calling>`.

Every task invocation will be given a unique identifier (an UUID), this
is the task id.

The ``delay`` and ``apply_async`` methods return an :class:`~@AsyncResult`
instance, that can be used to keep track of the tasks execution state.
But for this you need to enable a :ref:`result backend <task-result-backends>` so that
the state can be stored somewhere.

Results are disabled by default because of the fact that there's no result
backend that suits every application, so to choose one you need to consider
the drawbacks of each individual backend. For many tasks
keeping the return value isn't even very useful, so it's a sensible default to
have. Also note that result backends aren't used for monitoring tasks and workers,
for that Celery uses dedicated event messages (see :ref:`guide-monitoring`).

If you have a result backend configured you can retrieve the return
value of a task:
"""

res = add.delay(2, 2)
print(res.get(timeout=1))
# 4

"""
You can find the task's id by looking at the :attr:`id` attribute:
"""

print(res.id)
# d6b3aea2-fb9b-4ebc-8da4-848818db9114

"""
You can also inspect the exception and traceback if the task raised an
exception, in fact ``result.get()`` will propagate any errors by default:
"""

try:
    res = add.delay(2)
    res.get(timeout=1)
except TypeError:
    traceback.print_exc()

# Traceback (most recent call last):
# File "<stdin>", line 1, in <module>
# File "/opt/devel/celery/celery/result.py", line 113, in get
#     interval=interval)
# File "/opt/devel/celery/celery/backends/rpc.py", line 138, in wait_for
#     raise meta['result']
# TypeError: add() takes exactly 2 arguments (1 given)

"""
If you don't wish for the errors to propagate then you can disable that
by passing the ``propagate`` argument:
"""

print(res.get(propagate=False))
# TypeError('add() takes exactly 2 arguments (1 given)',)

"""
In this case it'll return the exception instance raised instead,
and so to check whether the task succeeded or failed you'll have to
use the corresponding methods on the result instance:
"""

print(res.failed())
# True

print(res.successful())
# False

"""
So how does it know if the task has failed or not?  It can find out by looking
at the tasks *state*:
"""

print(res.state)
# 'FAILURE'

"""
A task can only be in a single state, but it can progress through several
states. The stages of a typical task can be::

    PENDING -> STARTED -> SUCCESS

The started state is a special state that's only recorded if the
:setting:`task_track_started` setting is enabled, or if the
``@task(track_started=True)`` option is set for the task.

The pending state is actually not a recorded state, but rather
the default state for any task id that's unknown: this you can see
from this example:
"""

from proj.celery import app

res = app.AsyncResult('this-id-does-not-exist')
print(res.state)
# 'PENDING'

"""
If the task is retried the stages can become even more complex.
To demonstrate, for a task that's retried two times the stages would be:

.. code-block:: text

    PENDING -> STARTED -> RETRY -> STARTED -> RETRY -> STARTED -> SUCCESS

To read more about task states you should see the :ref:`task-states` section
in the tasks user guide.

Calling tasks is described in detail in the
:ref:`Calling Guide <guide-calling>`.
"""
