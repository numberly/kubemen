.. image:: https://raw.githubusercontent.com/numberly/kubemen/master/artwork/logo.png
   :target: https://youtu.be/PVjA0y78_EQ

|

.. image:: https://img.shields.io/github/v/tag/numberly/kubemen
   :target: https://github.com/numberly/kubemen/releases
.. image:: https://img.shields.io/github/license/numberly/kubemen.svg
   :target: https://github.com/numberly/kubemen/blob/master/LICENSE
.. image:: https://img.shields.io/docker/cloud/build/numberly/kubemen
   :target: https://hub.docker.com/r/numberly/kubemen
.. image:: https://img.shields.io/travis/numberly/kubemen/master?label=travis%20build
   :target: https://travis-ci.org/numberly/kubemen
.. image:: https://img.shields.io/coveralls/numberly/kubemen.svg
   :target: https://coveralls.io/github/numberly/kubemen
.. image:: https://readthedocs.org/projects/kubemen/badge
   :target: http://kubemen.readthedocs.io

|

*They watch on your Kubernetes cluster…*

Kubemen is a `Kubernetes validating admission webhook`_ that sends
notifications when a resource changes on your cluster, heavily influenced by the
*Watchmen (2009)* movie.

Currently supported channels:

* Mattermost_
* emails

Documentation: https://kubemen.readthedocs.io


Installation
============

Kubernetes
----------

Requirements:

* RBAC being enabled on your cluster
* the ValidatingAdmissionWebhook admission controller being enabled too
* you being an administrator of the cluster

If these requirements are fulfilled, installing Kubemen on your cluster is
pretty straightforward:

* setup the namespace and RBAC stuff with:

.. code-block:: bash

    $ kubectl apply -f deploy/configuration.yaml

* create TLS certificates for the service and sign them through the CSR API:

.. code-block:: bash

    $ sh deploy/create-cert.sh

* deploy Kubemen:

.. code-block:: bash

    $ cat deploy/kubemen.yaml | sh deploy/patch-ca-bundle.sh | kubectl apply -f -


Locally
-------

If you want to hack on Kubemen:

* create and activate a virtualenv_:

.. code-block:: bash

    $ virtualenv -ppython3 .venv
    $ .venv/bin/activate

* install the application requirements with pip_:

.. code-block:: bash

    (.venv) $ pip install -r requirements.txt

* run it with:

.. code-block:: bash

    (.venv) $ python run.py


Tests
=====

To run Kubemen tests:

* install Kubemen locally (see above);
* install developers requirements with ``pip install -r dev-requirements.txt``;
* run ``pytest``.


License
=======

MIT


.. _Kubernetes validating admission webhook: https://kubernetes.io/blog/2019/03/21/a-guide-to-kubernetes-admission-controllers/
.. _Mattermost: https://mattermost.com/
.. _pip: https://pip.pypa.io/en/stable/quickstart/
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
