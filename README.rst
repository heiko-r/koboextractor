KoboExtractor
=============

This Python package provides a wrapper around part of the KoBoToolbox kpi API,
with the main goal being to ease the downloading of survey responses. It
provides methods to download data from the KoBoToolbox kpi API
(e.g. https://kf.kobotoolbox.org/ or https://kc.humanitarianresponse.info/) and
to rearrange this data into useable structures.

Installation
------------

KoboExtractor requires Python 3.6+.

Simply install from PyPI with::

	pip3 install koboextractor

Example usage
-------------

In this example, response data is downloaded from KoBoToolbox and arranged in a
form that is convenient for further processing, e.g. for storing in a different
database or uploading to Google Sheets.

Import and initialise the KoboExtractor:

.. code-block:: python

	from koboextractor import KoboExtractor
	kobo = KoboExtractor(KOBO_TOKEN, 'https://kf.kobotoolbox.org/api/v2', debug=debug)

Get the unique ID of the first asset in your KoBoToolbox account:

.. code-block:: python

	assets = kobo.list_assets()
	asset_uid = assets['results'][0]['uid']

Information on the questions and choices in your survey can be obtained with:

.. code-block:: python

	asset = kobo.get_asset(asset_uid)
	choice_lists = kobo.get_choices(asset)
	questions = kobo.get_questions(asset=asset, unpack_multiples=True)

``questions`` is a dictionary of the form:

.. code-block:: python

	{
		GROUP_CODE: {
			'label': GROUP_LABEL,
			'questions': {
				QUESTION_CODE: {
					'type': QUESTION_TYPE,
					'sequence': SEQUENCE_NUMBER,
					'label': QUESTION_LABEL,
					'list_name': CHOICE_LIST_NAME,
				}
			}
		}
	}

``choices`` is a dictionary of the form:

.. code-block:: python

	{
		LIST_NAME: {
			'label': CHOICE_LABEL,
			'sequence': SEQUENCE_NUMBER
		}
	}

One way to delete questions you're not interested in could be:

.. code-block:: python

	# Remove all questions without labels or of the following types
	delete_types = ['start', 'end', 'today', 'begin_group', 'end_group', 'calculate']
	for question_group, question_group_dict in questions.items():
		# The [] part is building a list of question_codes where the question type is in the above delete list
		for question_code in [question_code for question_code, question_dict in question_group_dict['questions'].items() if question_dict['type'] in delete_types]: del questions[question_group]['questions'][question_code]
		for question_code in [question_code for question_code, question_dict in question_group_dict['questions'].items() if 'label' not in question_dict]: del questions[question_group]['questions'][question_code]
	# delete empty question groups
	for question_group in [question_group for question_group, question_group_dict in questions.items() if not question_group_dict['questions']]: del questions[question_group]

If you need a list of questions in the order of their appearance in the survey,
use:

.. code-block:: python

	# Put all questions from all groups into one list
	all_questions = []
	for question_group_code, question_group_dict in questions.items():
		for question_code, question_dict in question_group_dict['questions'].items():
			if 'label' in question_dict:
				label = question_dict['label']
			else:
				label = question_code
			all_questions.append({
				'group_code': question_group_code,
				'question_code': question_code,
				'question_label': label,
				'sequence': question_dict['sequence']
			})
	# Sort the questions by their order in the survey
	sorted_questions = sorted(all_questions, key = lambda question: question['sequence'])

Download all responses submitted after a certain point in time:

.. code-block:: python

	new_data = kobo.get_data(asset_uid, submitted_after='2020-05-20T17:29:30')

The number of downloaded results is available in ``new_data['count']``.

``new_data`` will be an unordered list of form submissions. We can sort this
list by submission time by calling:

.. code-block:: python

	new_results = kobo.sort_results_by_time(new_data['results'])

Each response (list item) is a dict with several metadata keys (such as
'_submission_time') and key/value pairs for each answered question in the form
of 'GROUP_CODE/QUESTION_CODE': 'ANSWER_CODE'. Map the question and answer labels
from your survey onto the coded answers in the responses:

.. code-block:: python

	labeled_results = []
	for result in new_results: # new_results is a list of list of dicts
		# Unpack answers to select_multiple questions
		labeled_results.append(kobo.label_result(unlabeled_result=result, choice_lists=choice_lists, questions=questions, unpack_multiples=True))

Documentation
-------------

The full documentation is available at https://koboextractor.readthedocs.io .