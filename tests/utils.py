# -*- coding: utf-8 -*-

"""
.. module:: utils.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Unit test utilities.

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import datetime
import os
import random
import uuid

import arrow
import requests



# Base API url.
BASE_URL = os.getenv("ERRATA_API")


def get_credentials():
    """Returns credentials to be passed to web service.

    """
    return os.getenv('ERRATA_WS_TEST_LOGIN'), \
           os.getenv('ERRATA_WS_TEST_TOKEN')


def assert_ws_response(
    url,
    response,
    status_code=requests.codes.OK,
    fields=set()
    ):
    """Asserts a response received from web-service.

    """
    # WS url.
    assert response.url.split('?')[0] == url.split('?')[0]

    # WS response HTTP status code.
    assert response.status_code == status_code, response.status_code

    # WS response = unicode.
    assert isinstance(response.text, unicode)

    # WS response has no cookies.
    assert len(response.cookies) == 0

    # WS response history is empty (i.e. no intermediate servers).
    assert len(response.history) == 0
    assert response.is_permanent_redirect == False
    assert response.is_redirect == False
    assert len(response.links) == 0

    # Default WS respponse headers.
    assert len(response.headers) >= 3
    for header in {
        # 'Content-Length',
        'Content-Type',
        'Date',
        'Server',
        'Vary'
        }:
        assert header in response.headers

    # WS response content must be utf-8 encoded JSON.
    if response.text:
        assert response.encoding.lower() == u'utf-8'
        content = response.json()
        assert isinstance(content, dict)
        for field in fields:
            assert field in content

        return content


# Integer assertion constants.
COMPARE_EXACT = "EXACT"
COMPARE_GT = "GT"
COMPARE_GTE = "GTE"
COMPARE_LTE = "LTE"
COMPARE_LT = "LT"
COMPARE_TYPES = (
    COMPARE_EXACT,
    COMPARE_GT,
    COMPARE_GTE,
    COMPARE_LT,
    COMPARE_LTE
)



def init(test, description, mod=None, suffix=None):
    """Initializes a test module prior to a test being executed.

    :param function test: The test to be run.
    :param str description: The description to be applied to the test.
    :param module mod: The associated document test module.

    """
    desc = "ES-DOC :: WS :: Test {}"
    if mod is not None and suffix is not None:
        desc += " - {} ({})"
        if hasattr(mod, "DOC_TYPE_KEY"):
            desc = desc.format(description, mod.DOC_TYPE_KEY, suffix)
        else:
            desc = desc.format(description, mod.__name__, suffix)
    elif mod is not None:
        desc += " - {}"
        if hasattr(mod, "DOC_TYPE_KEY"):
            desc = desc.format(description, mod.DOC_TYPE_KEY)
        else:
            desc = desc.format(description, mod.__name__)
    elif suffix is not None:
        desc += " ({})"
        desc = desc.format(description, suffix)
    else:
        desc = desc.format(description)
    test.description = desc


def get_boolean():
    """Returns a random boolean for testing purposes.

    """
    return True


def get_date():
    """Returns a random integer for testing purposes.

    """
    return datetime.datetime.now()


def get_int(lower=0, upper=9999999):
    """Returns a random integer for testing purposes.

    """
    return random.randint(lower, upper)


def get_float():
    """Returns a random float for testing purposes.

    """
    return random.random()


def get_string(length):
    """Returns a random string for testing purposes.

    """
    return str(uuid.uuid1())[:length]


def get_unicode(length):
    """Returns a random unicode for testing purposes.

    """
    return unicode(uuid.uuid1())[:length]


def get_uuid():
    """Returns a uuid for testing purposes.

    """
    return str(uuid.uuid1())


def assert_iter(collection,
                length=-1,
                item_type=None,
                length_compare=COMPARE_GTE):
    """Asserts an object collection.

    :param collection: An object collection.
    :type collection: list

    :param length: Collection size.
    :type length: int

    :param length: Collection size comparason operator.
    :type length: str

    :param item_type: Type that each collection item should sub-class.
    :type item_type: class or None

    """
    assert_object(collection)
    assert iter(collection) is not None
    if length != -1:
        assert_int(len(collection), length, length_compare)
    if item_type is not None:
        if isinstance(collection, dict):
            collection = collection.values()
        for instance in collection:
            assert_object(instance, item_type)


def assert_in_collection(collection, item_attr, items):
    """Asserts an item is within a collection.

    :param collection: A collection.
    :type collection: list

    :param item: A collection item.
    :type item: object

    """
    try:
        iter(items)
    except TypeError:
        items = [items]
    targets = None
    if item_attr is not None:
        targets = [getattr(i, item_attr) for i in collection]
    else:
        targets = collection
    for item in items:
        assert item in targets, item


def assert_none(instance):
    """Asserts an instance is none.

    :param instance: An object for testing.
    :type instance: object

    """
    assert instance is None, \
           "Instance null mismatch : actual = {0} - {1} :: expected = None" \
           .format(type(instance), instance)


def assert_object(instance, instance_type=None):
    """Asserts an object instance.

    :param instance: An object for testing.
    :type instance: object

    :param instance_type: Type that object must either be or sub-class from.
    :type instance_type: class

    """
    assert instance is not None
    if instance_type is not None:
        assert isinstance(instance, instance_type), \
               "Instance type mismatch : actual = {0} :: expected = {1}" \
               .format(type(instance), instance_type)


def assert_objects(instance1, instance2):
    """Asserts that 2 object instances are equal.

    :param instance1: An object for testing.
    :type instance1: object

    :param instance2: An object for testing.
    :type instance2: object

    """
    assert instance1 is not None, "Only non-null objects are comparable."
    assert instance2 is not None, "Only non-null objects are comparable."
    assert instance1 == instance2, "Instances are not equal"


def assert_bool(actual, expected):
    """Asserts a boolean.

    :param actual: An expression evaluaed as a boolean.
    :type actual: expr | bool

    :param expected: An expression evaluaed as a boolean.
    :type actual: expr | bool

    """
    assert bool(actual) == bool(expected)


def assert_str(actual, expected, startswith=False):
    """Asserts a string.

    :param actual: A string.
    :type actual: str

    :param expected: Expected string value.
    :type expected: str

    :param startswith: Flag indicating whether to perform startswith test.
    :type startswith: bool

    """
    # Format.
    actual = str(actual).strip()
    expected = str(expected).strip()

    # Assert.
    if startswith == False:
        assert actual == expected, \
               "String mismatch : actual = {0} :: expected = {1}" \
               .format(actual, expected)
    else:
        assert actual.startswith(expected) == True, \
               "String startswith mismatch : actual = {0} :: expected = {1}" \
               .format(actual, expected)


def assert_unicode(actual, expected):
    """Asserts a unicode.

    :param actual: A unicode.
    :type actual: str

    :param expected: Expected unicode value.
    :type expected: str

    """
    assert_object(actual, unicode)
    assert_object(expected, unicode)
    assert actual == expected, \
           "Unicode mismatch : actual = {0} :: expected = {1}" \
           .format(actual, expected)


def assert_date(actual, expected):
    """Asserts a datetime.

    :param actual: A date.
    :type actual: str

    :param expected: Expected date value.
    :type expected: str

    """
    if not isinstance(actual, datetime.datetime):
        actual = arrow.get(actual)
    if not isinstance(expected, datetime.datetime):
        expected = arrow.get(expected)

    assert actual == expected, \
           "Date mismatch : actual = {0} :: expected = {1}" \
           .format(actual, expected)


def assert_float(actual, expected):
    """Asserts a float.

    :param float actual: Actual float value.
    :param float expected: Expected float value.

    """
    assert_object(actual, float)
    assert_object(expected, float)
    assert actual == expected, \
           "Float mismatch : actual = {0} :: expected = {1}" \
           .format(actual, expected)


def assert_path(actual):
    """Asserts a filepath.

    :param str actual: Actual file path.

    """
    assert_bool(os.path.exists(actual), True)


def assert_int(actual, expected, assert_type=COMPARE_EXACT, msg=None):
    """Asserts an integer.

    :param actual: An integer.
    :type actual: int

    :param expected: Expected integer value.
    :type expected: int

    """
    # Parse actual value.
    # ... convert string
    if type(actual) == str:
        actual = int(actual)
    # ... collection length checks
    else:
        try:
            iter(actual)
        except TypeError:
            pass
        else:
            actual = len(actual)

    if assert_type == COMPARE_EXACT:
        assert expected == actual, "{0} != {1} {2}".format(actual, expected, msg)
    elif assert_type == COMPARE_GT:
        assert expected > actual, "{0} !> {1} {2}".format(actual, expected, msg)
    elif assert_type == COMPARE_GTE:
        assert expected >= actual, "{0} !>= {1} {2}".format(actual, expected, msg)
    elif assert_type == COMPARE_LT:
        assert expected < actual, "{0} !< {1} {2}".format(actual, expected, msg)
    elif assert_type == COMPARE_LTE:
        assert expected <= actual, "{0} !<= {1} {2}".format(actual, expected, msg)
    else:
        assert expected == actual, "{0} != {1} {2}".format(actual, expected, msg)


def assert_int_negative(actual, expected):
    """Negatively asserts an integer.

    :param actual: An integer.
    :type actual: int

    :param expected: Another integer value.
    :type expected: int

    """
    assert actual != expected


def assert_uuid(actual, expected):
    """Asserts a uuid.

    :param actual: A date.
    :type actual: str

    :param expected: Expected uuid value.
    :type expected: str

    """
    if isinstance(actual, uuid.UUID) == False:
        actual = uuid.UUID(actual)
    if isinstance(expected, uuid.UUID) == False:
        expected = uuid.UUID(expected)

    assert actual == expected, "{0} != {1}".format(actual, expected)
