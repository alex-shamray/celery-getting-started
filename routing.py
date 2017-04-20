from proj.celery import app

"""
Routing
=======

Celery supports all of the routing facilities provided by AMQP,
but it also supports simple routing where messages are sent to named queues.

The :setting:`task_routes` setting enables you to route tasks by name
and keep everything centralized in one location:
"""

app.conf.update(
    task_routes = {
        'proj.tasks.add': {'queue': 'hipri'},
    },
)

"""
You can also specify the queue at runtime
with the ``queue`` argument to ``apply_async``:
"""

from proj.tasks import add
add.apply_async((2, 2), queue='hipri')

"""
You can then make a worker consume from this queue by
specifying the :option:`celery worker -Q` option:

.. code-block:: console

    $ celery -A proj worker -Q hipri

You may specify multiple queues by using a comma separated list,
for example you can make the worker consume from both the default
queue, and the ``hipri`` queue, where
the default queue is named ``celery`` for historical reasons:

.. code-block:: console

    $ celery -A proj worker -Q hipri,celery

The order of the queues doesn't matter as the worker will
give equal weight to the queues.

To learn more about routing, including taking use of the full
power of AMQP routing, see the :ref:`Routing Guide <guide-routing>`.
"""
