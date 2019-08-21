.. image:: https://raw.githubusercontent.com/numberly/kubemen/master/logo.png
   :target: https://youtu.be/PVjA0y78_EQ

|

.. image:: https://img.shields.io/github/v/release/numberly/kubemen
   :target: https://github.com/numberly/thingy/releases
.. image:: https://img.shields.io/github/license/numberly/kubemen.svg
   :target: https://github.com/numberly/kubemen/blob/master/LICENSE
.. image:: https://img.shields.io/docker/build/numberly/kubemen
   :target: https://hub.docker.com/r/numberly/kubemen
.. image:: https://img.shields.io/travis/numberly/kubemen?label=travis%20build
   :target: https://travis-ci.org/numberly/kubemen
.. image:: https://img.shields.io/coveralls/numberly/kubemen.svg
   :target: https://coveralls.io/github/numberly/kubemen
.. image:: https://readthedocs.org/projects/kubemen/badge
   :target: http://kubemen.readthedocs.io

|

*They watch on your Kubernetes cluster…*

Kubemen is a `Kubernetes validating admission webhook`_ that sends
notifications when a resource change on your cluster, heavily influenced by the
*Watchmen (2009)* movie.

Currently supported channels:

* Mattermost_
* emails

Documentation: https://kubemen.readthedocs.io


Installation
============

Kubernetes
----------

.. code-block:: bash

    $ kubectl apply -f https://raw.githubusercontent.com/numberly/kubemen/master/kubernetes.yaml

Docker
------

.. code-block:: bash

    $

Locally
-------

1. clone this git repository

.. code-block:: bash

    $ git clone git@github.com:numberly/kubemen kubemen
    $ cd kubemen

2. create and activate a virtualenv_

.. code-block:: bash

    $ virtualenv -ppython3 .venv
    $ .venv/bin/activate

3. install the application requirements with pip_

.. code-block:: bash

    (.venv) $ pip install -r requirements.txt

You should now be able to run it with:

.. code-block:: bash

    (.venv) $ python run.py


Tests
=====

To run Kubemen tests:

* install Kubemen locally (see above);
* install developers requirements with ``pip install -r requirements.txt``;
* run ``pytest``.


License
=======

MIT


.. _Kubernetes validating admission webhook: https://kubernetes.io/blog/2019/03/21/a-guide-to-kubernetes-admission-controllers/
.. _Mattermost: https://mattermost.com/
.. _pip: https://pip.pypa.io/en/stable/quickstart/
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
