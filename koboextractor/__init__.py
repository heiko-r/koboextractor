import requests
from typing import Any, Dict, List

class KoboExtractor:
    """Extracts collected data from KoBoToolbox.
    
    This class provides methods to connect to the kpi API of
    KoBoToolbox, access information about surveys, their questions, choices,
    and responses.
        
    Attributes:
        token: Your authentication token, which can be obtained from
            https://kf.kobotoolbox.org/token/.
        endpoint: The KoBoToolbox kpi API endpoint, e.g.
            https://kf.kobotoolbox.org/api/v2 or
            https://kobo.humanitarianresponse.info/api/v2.
        debug: Set to True to enable debugging output. Default: False.
    """
    def __init__(self, token: str, endpoint: str, debug: bool = False) -> None:
        """Initialises the KoboExtractor with token and endpoint.
        
        Args:
            token: Your authentication token, which can be obtained from
                https://kf.kobotoolbox.org/token/.
            endpoint: The KoBoToolbox kpi API endpoint, e.g.
                https://kf.kobotoolbox.org/api/v2 or
                https://kobo.humanitarianresponse.info/api/v2.
            debug: Set to True to enable debugging output. Default: False.
        """
        self.token = token
        self.endpoint = endpoint
        self.debug = debug
        pass
    
    
    def list_assets(self) -> Dict[str, Any]:
        """Lists all assets (surveys).
        
        Lists all assets (surveys) in the associated KoBoToolbox account.
        
        Returns:
            A dict containing information about your assets.
            Log into KoBoToolbox and visit
            https://kf.kobotoolbox.org/api/v2/assets/ to see a description.
        """
        url = f'{self.endpoint}/assets.json'
        headers = {'Authorization': f'Token {self.token}'}
        if self.debug: print(f'KoboExtractor.list_assets: Calling {url}')
        response = requests.get(url, headers=headers)
        return response.json()
    
    
    def get_asset(self, asset_uid: str) -> Dict[str, Any]:
        """Gets information on an asset (survey).
        
        Gets all information on an asset (survey) in the associated KoBoToolbox
        account.
        
        Args:
            asset_uid: Unique ID of the asset. Obtainable e.g. through
                ``list_assets()['results'][i]['uid']`` (for your first asset, use
                ``i=0``).
        
        Returns:
            A dict containing information about your asset.
            Log into KoBoToolbox and visit
            https://kf.kobotoolbox.org/api/v2/assets/YOUR_ASSET_UID/ to see a
            description.
        """
        url = f'{self.endpoint}/assets/{asset_uid}.json'
        headers = {'Authorization': f'Token {self.token}'}
        if self.debug: print(f'KoboExtractor.get_asset: Calling {url}')
        response = requests.get(url , headers=headers)
        return response.json()
    
    
    def get_data(self,
                 asset_uid,             # type: str
                 query=None,            # type: str
                 start=None,            # type: int
                 limit=None,            # type: int
                 submitted_after=None,  # type: str
                 ):
        # type: (...) -> Dict[str, Any]
        """Gets the data (responses) of an asset (survey).
        
        Gets all information on an asset (survey) in the associated KoBoToolbox
        account.
        
        Args:
            asset_uid: Unique ID of the asset. Obtainable e.g. through
                ``list_assets()['results'][i]['uid']`` (for your first asset, use
                i=0).
            query: Query string in the form ``'{"field":"value"}'`` or
                ``'{"field":{"op": "value"}}'``, e.g.
                ``'{"_submission_time": {"$gt": "2020-05-14T14:36:20"}}'``. See
                https://docs.mongodb.com/manual/reference/operator/query/ for
                operators.
            start: Index (zero-based) from which the results start (default: 0).
            limit: Number of results per page (max: 30000, default: 30000).
            submitted_after: Shorthand to query for submission time. String of
                date and time in ISO format (e.g. 2020-05-14T14:36:20, results)
                in query
                ``'{"_submission_time": {"$gt": "2020-05-14T14:36:20"}}'``.
                Ignored when combined with 'query'.
        
        Returns:
            A dict containing the data associated with the asset. For a survey
            asset, the key 'count' provides the number of responses. The key
            'results' contains a list of responses. Each response is a dict with
            several metadata keys (such as '_submission_time') and key/value
            pairs for each answered question in the form of
            'GROUP_CODE/QUESTION_CODE': 'ANSWER_CODE'.
            Log into KoBoToolbox and visit
            https://kf.kobotoolbox.org/api/v2/assets/YOUR_ASSET_UID/data/ for a
            more detailed description.
        """
        if self.debug and query and submitted_after:
            print("KoboExtractor.get_data(): Ignoring argument "
                  "'submitted_after' because 'query' is specified.")
        url = f'{self.endpoint}/assets/{asset_uid}/data.json'
        
        if query or start or limit or submitted_after:
            url += '?'
        if query:
            url += f'query={query}'
        elif submitted_after:
            url += f'query={{"_submission_time": {{"$gt": "{submitted_after}"}}}}'
        
        if (query or submitted_after) and (start or limit):
            url += '&'
        
        if start:
            url += f'start={start}'
            if limit:
                url += '&'
        if limit:
            url += f'limit={limit}'
        
        headers = {'Authorization': f'Token {self.token}'}
        if self.debug: print(f'KoboExtractor.get_data: Calling {url}')
        response = requests.get(url, headers=headers)
        return response.json()
    
    
    def get_choices(self,
                    asset,  # type: Dict[str, Any]
                    ):
        # type: (...) -> Dict[str, Dict[str, Dict[str, str]]]
        """Groups the choices (answer options) of a survey into a dict.
        
        Groups all the choices (answer options) of a survey into a dict,
        arranged by their list. A 'sequence' number is added to allow restoring
        the original order of the choices from the inherently unordered dict.
        
        Args:
            asset: A dict as returned by ``get_asset()``.
        
        Returns:
            A dict of the form::
            
                {
                    LIST_NAME: {
                        'label': CHOICE_LABEL,
                        'sequence': SEQUENCE_NUMBER
                    }
                }
            
            where CHOICE_LABEL is the label (text) of the choice in the survey's
            default language, and SEQUENCE_NUMBER is an incrementing number that
            can be used to restore the order of the choices in the survey from
            this unordered dict.
        """
        choice_lists = {}
        sequence = 0
        for choice in asset['content']['choices']:
            if choice['list_name'] not in choice_lists:
                choice_lists[choice['list_name']] = {}
            choice_lists[choice['list_name']][choice['name']] = {
                'label': choice['label'][0],
                'sequence': sequence
            }
            sequence += 1
        return choice_lists
    
    
    def get_questions(self,
                      asset,            # type: Dict[str, Any]
                      unpack_multiples, # type: bool
                      ):
        # type: (...) -> Dict[str, Dict[str, str]]
        """Groups the choices (answer options) of a survey into a dict.
        
        Groups all the choices (answer options) of a survey into a dict,
        arranged by their list. A 'sequence' number is added to allow restoring
        the original order of the choices from the inherently unordered dict.
        
        Args:
            asset: A dict as returned by ``get_asset()``.
            unpack_multiples: If True, the corresponding choices from
                ``get_choices()`` are added as subsequent questions following a
                multiple choice question (type 'select_multiple'). The type of
                these additional questions is set to 'select_multiple_option'.
        
        Returns:
            A dict of the form::
            
                {
                    GROUP_CODE: {
                        'label': GROUP_LABEL,
                        'repeat': True/False,
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
            
            where GROUP_LABEL and QUESTION_LABEL are the labels (text) of the
            group or question in the survey's default language. SEQUENCE_NUMBER
            is an incrementing number that can be used to restore the order of
            the questions in the survey from this unordered dict.
            
            Depending on the question, not all keys may be present.
            
            An additional question of the type '_or_other' is inserted after any
            question which type ends in '_or_other', to cover the reponses to
            such questions.
        """
        if unpack_multiples:
            choices = self.get_choices(asset)
        qns = {}
        group_code = None
        group_label = None
        sequence = 0
        for qn in asset['content']['survey']:
            # qn['name'] or qn['$autoname'] is the question code
            # Assuming every question has a type (so far it has been true)
            
            if 'name' in qn:
                name = qn['name']
            elif '$autoname' in qn:
                name = qn['$autoname']
            else:
                name = None
            
            # Adding new question groups
            if qn['type'] == 'begin_group' or qn['type'] == 'begin_repeat':
                group_code = name
                if 'label' in qn:
                    group_label = qn['label'][0]
            if group_code not in qns:
                qns[group_code] = {}
                qns[group_code]['label'] = group_label
                if qn['type'] == 'repeat_group':
                    qns[group_code]['repeat'] = True
                else:
                    qns[group_code]['repeat'] = False
                qns[group_code]['questions'] = {}
            
            # Adding new questions to the current group
            if name:
                qns[group_code]['questions'][name] = {}
                qns[group_code]['questions'][name]['type'] = qn['type']
                qns[group_code]['questions'][name]['sequence'] = sequence
                if 'label' in qn:
                    qns[group_code]['questions'][name]['label'] = qn['label'][0]
                if 'select_from_list_name' in qn:
                    qns[group_code]['questions'][name]['list_name'] = qn['select_from_list_name']
            elif qn['type'] == 'end_group' or qn['type'] == 'end_repeat':
                group_code = None
                group_label = None
            else:
                raise Exception(f'Question without name or $autoname, type: { qn["type"] }')
            
            if unpack_multiples and qn['type'] == 'select_multiple':
                list_name = qn['select_from_list_name']
                sorted_choices = sorted(choices[list_name].items(),
                                        key=lambda choice: choice[1]['sequence'])
                for choice in sorted_choices:
                    sequence += 1
                    qns[group_code]['questions'][f'{ name }/{ choice[0] }'] = {}
                    qns[group_code]['questions'][f'{ name }/{ choice[0] }']['label'] = choice[1]['label']
                    qns[group_code]['questions'][f'{ name }/{ choice[0] }']['type'] = 'select_multiple_option'
                    qns[group_code]['questions'][f'{ name }/{ choice[0] }']['sequence'] = sequence
            if '_or_other' in qn and qn['_or_other']:
                sequence += 1
                qns[group_code]['questions'][f'{ name }_other'] = {
                    'type': '_or_other',
                    'label': f'{ name }_other',
                    'sequence': sequence
                }
            
            sequence += 1
        return qns
    
    
    def sort_results_by_time(self,
                             unsorted_results,  # type: List[Dict[str, Any]]
                             reverse=False,     # type: bool
                             ):
        # type: (...) -> List[Dict[str, Any]]
        """Sorts an unordered list of responses by their submission time.
        
        Sorts a list of responses in random order (e.g. as obtained by
        ``get_data(asset_uid)['results']`` by the value of their
        ``_submission_time`` key.
        
        Example::
            
            from koboextractor import KoboExtractor
            kobo = KoboExtractor(KOBO_TOKEN, 'https://kf.kobotoolbox.org/api/v2')
            assets = kobo.list_assets()
            asset_uid = assets['results'][0]['uid']
            new_data = kobo.get_data(asset_uid)
            new_results = kobo.sort_results_by_time(new_data['results'])
        
        Args:
            unsorted_results: A list of results as returned by
                ``kobo.get_data(asset_uid)['results']``.
            reverse: If True, sort in descending order. Default: False.
        
        Returns:
            A list of results as provided in ``unsorted_results``, but sorted by
            the value of their ``_submission_time`` key.
        """
        sorted_results = sorted(unsorted_results,
                                key=lambda result: result['_submission_time'],
                                reverse=reverse)
        return sorted_results
    
    
    def label_result(self,
                     unlabeled_result,  # type: Dict[str, Any]
                     choice_lists,      # type: Dict[str, Dict[str, str]]
                     questions,         # type: Dict[str, Dict[str, str]]
                     unpack_multiples,  # type: bool
                     ):
        # type: (...) -> Dict[str, Dict[str, Any]]
        """Adds labels for questions and answers to a response.
        
        Adds labels corresponding the the question group codes, question codes
        and answer codes to a response.
        
        Example:
            ::
            
                from KoboExtractor import KoboExtractor
                kobo = KoboExtractor(KOBO_TOKEN, 'https://kf.kobotoolbox.org/api/v2')
                
                assets = kobo.list_assets()
                asset_uid = assets['results'][0]['uid']
                asset = kobo.get_asset(asset_uid)
                choice_lists = kobo.get_choices(asset)
                questions = kobo.get_questions(asset=asset, unpack_multiples=True)
                
                asset_data = kobo.get_data(asset_uid)
                results = kobo.sort_results_by_time(asset_data['results'])
                labeled_results = []
                for result in results:
                    labeled_results.append(kobo.label_result(unlabeled_result=result, choice_lists=choice_lists, questions=questions, unpack_multiples=True))
            
        Args:
            unlabeled_result: A single result (dict) of the form::
                
                    {
                        'GROUP_CODE/QUESTION_CODE': 'ANSWER_CODE',
                        'REPEAT_GROUP_CODE': [
                            {
                                'REPEAT_GROUP_CODE/QUESTION_CODE': 'ANSWER_CODE',
                            }
                        ],
                        'METADATA_KEY': 'METADATA_VALUE'
                    }
                
                (e.g. one of the list items in
                ``get_data(asset_uid)['results']``).
            
            choice_lists: Dict of choice lists as returned by
                ``get_choices(asset)``.
            questions: Dict of questions as returned by
                ``get_questions(asset)``
            unpack_multiples: If True, the corresponding choices from
                ``get_choices()`` are added as subsequent questions following a
                multiple choice question (type 'select_multiple').
        
        Returns:
            A dict of the form::
            
                {
                    'meta': {
                        'start': '2020-05-15T08:07:24.705+08:00',
                        '_version_': 'vf4kqJPWTbsMrZSw5RZQ7H',
                        '_submission_time': '2020-05-15T00:17:51',
                        ...
                    },
                    'questions': {
                        GROUP_CODE: {
                            'label': 'Group label',
                            'questions': {
                                QUESTION_CODE: {
                                    'label': 'Question label',
                                    'answer_code': ANSWER_CODE,
                                    'answer_label': 'Answer label',
                                    'sequence': QUESTION_SEQUENCE
                                },
                                {
                                    ...
                                }
                            }
                        },
                        REPEAT_GROUP_CODE: {
                            'label': 'Group label',
                            'repeats': {
                                0: {
                                    QUESTION_CODE: {
                                        'label': 'Question label',
                                        'answer_code': ANSWER_CODE,
                                        'answer_label': 'Answer label',
                                        'sequence': QUESTION_SEQUENCE
                                    },
                                    {
                                        ...
                                    }
                                },
                                1: {
                                    ...
                                }
                            }
                        },
                        ...
                    }
                }
            
            QUESTION_SEQUENCE reflects the order of the questions (and
            choices) in the survey.
        """
        def label_question(group_code, question_code, value, questions, choice_lists, unpack_multiples):
            # Add and label the question
            tmp_qn = {}
            if not (question_code in questions[group_code]['questions'] and
                    'label' in questions[group_code]['questions'][question_code]):
                # Cannot label this question and answer
                tmp_qn['label'] = question_code
                tmp_qn['answer_code'] = value
                tmp_qn['answer_label'] = value
            else:
                tmp_qn['sequence'] = questions[group_code]['questions'][question_code]['sequence']
                tmp_qn['label'] = questions[group_code]['questions'][question_code]['label']
                tmp_qn['answer_code'] = value
                if questions[group_code]['questions'][question_code]['type'] == 'select_one':
                    try:
                        # get answer label from choice list
                        list_name = questions[group_code]['questions'][question_code]['list_name']
                        tmp_qn['answer_label'] = choice_lists[list_name][value]['label']
                    except KeyError:
                        # Cannot label this answer
                        tmp_qn['answer_label'] = value
                elif questions[group_code]['questions'][question_code]['type'] == 'select_multiple':
                    list_name = questions[group_code]['questions'][question_code]['list_name']
                    try:
                        # get individual answer labels from choice list and
                        # concatenate them into this question's answer label
                        answer_label = ''
                        for split_answer_code in value.split():
                            answer_label = answer_label + choice_lists[list_name][split_answer_code]['label'] + ';'
                        tmp_qn['answer_label'] = answer_label
                    except KeyError:
                        # Cannot label this answer
                        tmp_qn['answer_label'] = value
                    if unpack_multiples:
                        # append additional 'questions' for the individual choices
                        for choice_code, choice_dict in choice_lists[list_name].items():
                            tmp_qn[f'{ question_code }/{ choice_code }'] = {}
                            tmp_qn[f'{ question_code }/{ choice_code }']['sequence'] = questions[group_code]['questions'][f'{ question_code }/{ choice_code }']['sequence']
                            tmp_qn[f'{ question_code }/{ choice_code }']['label'] = choice_dict['label']
                            tmp_qn[f'{ question_code }/{ choice_code }']['answer_code'] = (int) (choice_code in value.split())
                            tmp_qn[f'{ question_code }/{ choice_code }']['answer_label'] = 'Yes' if choice_code in value.split() else 'No'
                else:
                    # no special treatment for simple types of questions
                    tmp_qn['answer_label'] = value
            return tmp_qn
        
        meta_keys_start = ('_', 'meta/', 'formhub/')
        
        tmp_meta = {}
        tmp_qns = {}
        for key, value in unlabeled_result.items():
            # there are various keys within an unlabeled_result dict, and not
            # all of them belong to survey questions:
            # key does not start with underscore, but contains '/' -> QUESTION_GROUP/QUESTION_TYPE
            # key does not start with underscore, but points to a list -> REPEAT_GROUP_CODE
            # any other case -> metadata
            group_code = ''
            question_code = ''
            if not key.startswith(meta_keys_start) and '/' in key:
                # regular question
                splitkey = key.split('/')
                group_code = splitkey[0]
                question_code = splitkey[1]
                # Add and label the group if not yet done
                if group_code not in tmp_qns:
                    tmp_qns[group_code] = {}
                    tmp_qns[group_code]['questions'] = {}
                    if group_code not in questions:
                        # Cannot label this group
                        tmp_qns[group_code]['label'] = group_code
                    else:
                        tmp_qns[group_code]['label'] = questions[group_code]['label']
                tmp_qns[group_code]['questions'][question_code] = label_question(group_code, question_code, value, questions, choice_lists, unpack_multiples)
            
            elif not key.startswith(meta_keys_start) and isinstance(value, list):
                # repeat group
                group_code = key
                # create repeat group and add label
                tmp_qns[group_code] = {}
                tmp_qns[group_code]['repeats'] = {}
                if group_code not in questions:
                    # Cannot label this group
                    tmp_qns[group_code]['label'] = group_code
                else:
                    tmp_qns[group_code]['label'] = questions[group_code]['label']
                tmp_qns[group_code]['repeats'] = {}
                i = 0
                for repeat_set in value:
                    tmp_qns[group_code]['repeats'][i] = {}
                    for repeat_key, repeat_value in repeat_set.items():
                        question_code = repeat_key.split('/')[1]
                        tmp_qns[group_code]['repeats'][i][question_code] = {}
                        tmp_qns[group_code]['repeats'][i][question_code] = label_question(group_code, question_code, repeat_value, questions, choice_lists, unpack_multiples)
                    i += 1
            
            else:
                # metadata
                tmp_meta[key] = value
        return {
            'meta': tmp_meta,
            'questions': tmp_qns
        }
    
