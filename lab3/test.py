import unittest
import lab3_module

from unittest.mock import patch, MagicMock
import datetime
from collections import Counter

class TestFunction(unittest.TestCase):
    @patch('requests.get')
    def test_api_successful_response(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'total': 709}
        mock_requests_get.return_value = mock_response

        test_params = {
            'jql': 'project = KAFKA AND status = Closed',
            'maxResults': 1000,
            'fields': 'created,resolutiondate'
        }

        result = lab3_module.api(test_params)
        mock_requests_get.assert_called_once_with('https://issues.apache.org/jira/rest/api/2/search', params=test_params)
        self.assertEqual(result, {'total': 709})

    def test_get_created_date(self):
        result = lab3_module.get_created_date(issue=lab3_module.data_for_test['issues'][0]) # "2023-10-26T09:27:48.000+0000"
        self.assertEqual(result, datetime.datetime(2023, 10, 26, 9, 27, 48, tzinfo=datetime.timezone.utc))

    def test_get_resolution_date(self):
        result = lab3_module.get_resolution_date(issue=lab3_module.data_for_test['issues'][0]) # "2023-10-11T10:05:15.000+0000"
        self.assertEqual(result, datetime.datetime(2023, 10, 11, 10, 5, 15, tzinfo=datetime.timezone.utc))

    def test_time_diff(self):
        time_start = "2023-09-20T19:30:14.000+0000"
        time_stop = "2023-09-20T23:43:48.000+0000"
        time_start_date = datetime.datetime.strptime(time_start, '%Y-%m-%dT%H:%M:%S.%f%z')
        time_stop_date = datetime.datetime.strptime(time_stop, '%Y-%m-%dT%H:%M:%S.%f%z')

        result = lab3_module.time_diff(time_start, time_stop)
        self.assertEqual(result, (time_stop_date - time_start_date).total_seconds() / (3600 * 24) ) # 0.17608796296296297

    def test_changelog(self):
        status = 'Open'
        result = lab3_module.changelog(lab3_module.data_for_test, status)
        self.assertEqual(result, [lab3_module.time_diff("2023-10-26T09:27:48.000+0000", "2023-11-07T05:52:16.650+0000")]) 

    def test_opened_closed_per_day(self):
        result = lab3_module.opened_closed_per_day(lab3_module.data_for_test)
        self.assertEqual(result, ( Counter([datetime.datetime(2023, 10, 26, 0, 0)]), Counter([datetime.datetime(2023, 11, 7, 0, 0)]) ) )

    def test_assignee_reporter(self):
        result = lab3_module.assignee_reporter(lab3_module.data_for_test())
        self.assertEqual(result, ["Apoorv Mittal"])

if __name__ == '__main__':
    unittest.main()

