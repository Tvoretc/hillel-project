Start project: python3 manage.py runserver

### Requirements

    - local.py
        - SECRET_KEY
        
test |latest-version|
=========================
|build-status| |python-support| |black|

Cerberus is a lightweight and extensible data validation library for Python.

.. code-block:: python

    >>> v = Validator({'name': {'type': 'string'}})
    >>> v.validate({'name': 'john doe'})
    True


