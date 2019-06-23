import datetime
import unittest

import server


class ServerTestCase(unittest.TestCase):

    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()

    def test_speeds(self):
        data = self.app.get('/speeds', follow_redirects=True)
        self.assertEqual(data.status_code, 400, "If get speeds without query params server should return "
                                                "400 status code")

        data = self.app.get('/speeds?start=2018-08-01T00:00:00Z&end=2018-08-07T00:00:00Z', follow_redirects=True)
        self.assertEqual(data.status_code, 200)

    def test_date_range(self):
        data = self.app.get('/speeds?start=2018-08-01T00:00:00Z&end=2018-08-07T00:00:00Z', follow_redirects=True)
        speeds_list = data.json
        date_range = [speed_info['date'] for speed_info in speeds_list]

        self.assertIn('2018-08-01T00:00:00Z', date_range, "Start date should be in date range list")
        self.assertIn('2018-08-07T00:00:00Z', date_range, "End date should be in date range list")
        self.assertNotIn('2018-08-08T00:00:00Z', date_range, "Next day should not be in date range list")
        self.assertEqual(len(date_range), 7, "Number of date in list should be equals 7")

    def test_error_cases_in_query_param(self):
        data = self.app.get('/speeds?start=2018-08-01T00:00:00Z', follow_redirects=True)
        self.assertEqual(data.json['message'], 'Not valid datetime string for `end` query param')
        self.assertEqual(data.status_code, 400, "If get speeds without end query param server should return "
                                                "400 status code")

        data = self.app.get('/speeds?end=2018-08-01T00:00:00Z', follow_redirects=True)
        self.assertEqual(data.json['message'], 'Not valid datetime string for `start` query param')
        self.assertEqual(data.status_code, 400, "If get speeds without start query param server should return "
                                                "400 status code")

        data = self.app.get('/speeds?end=2018-08-01T00:00:00Z&start=2018-13-01T00:00:00Z', follow_redirects=True)
        self.assertEqual(data.json['message'], 'Not valid datetime string for `start` query param')
        self.assertEqual(data.status_code, 400, "If get speeds with broken datetime format mi should"
                                                " get 400 status code")

    def test_unavailable_day(self):
        future_day = (datetime.datetime.now() + datetime.timedelta(days=10)).strftime(format='%Y-%m-%dT%H:%M:%SZ')
        data = self.app.get(f'/speeds?start={future_day}&end={future_day}', follow_redirects=True)
        self.assertEqual(data.json['message'], f'no sample found for date {future_day}')
        self.assertEqual(data.status_code, 404)

    def test_fields_in_response(self):
        data = self.app.get('/speeds?start=2018-08-01T00:00:00Z&end=2018-08-07T00:00:00Z', follow_redirects=True)
        first_element = data.json[0]
        self.assertTrue(first_element.get('north', False), 'Speeds endpoint must return `north` field')
        self.assertTrue(first_element.get('west', False), 'Speeds endpoint must return `west` field')
        self.assertFalse(first_element.get('temp', False), 'Speeds endpoint must not return `temp` field')

        data = self.app.get('/temperatures?start=2018-08-01T00:00:00Z&end=2018-08-07T00:00:00Z', follow_redirects=True)
        first_element = data.json[0]
        self.assertFalse(first_element.get('north', False), 'Temperatures endpoint must not return `north` field')
        self.assertFalse(first_element.get('west', False), 'Temperatures endpoint must not return `west` field')
        self.assertTrue(first_element.get('temp', False), 'Temperatures endpoint must return `temp` field')

        data = self.app.get('/weather?start=2018-08-01T00:00:00Z&end=2018-08-07T00:00:00Z', follow_redirects=True)
        first_element = data.json[0]
        self.assertTrue(first_element.get('north', False), 'Weather endpoint must return `north` field')
        self.assertTrue(first_element.get('west', False), 'Weather endpoint must return `west` field')
        self.assertTrue(first_element.get('temp', False), 'Weather endpoint must return `temp` field')


if __name__ == '__main__':
    unittest.main()
