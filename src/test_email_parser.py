from datetime import datetime
from email_parser import EmailParser

import unittest


class EmailParserTestCase(unittest.TestCase):
    def test_sample(self):
        with open('../data/provider_email.txt') as f:
            result = EmailParser.parse('noc@fiberprovider.com', f.read())
        self.assertEqual('PWIC12345', result.update_id)
        self.assertEqual('PWIC45678', result.cancel_id)
        self.assertEqual('IC-99999', result.service_id)
        self.assertEqual(datetime(2019, 4, 9, 6), result.begin)
        self.assertEqual(datetime(2019, 4, 9, 10), result.end)
        self.assertEqual('Planned Work PWIC12345 Notification from Fiber Provider to AwesomeCorp, 2019-Apr-09 06:00 - 2019-Apr-09 10:00 UTC', result.subject)
        self.assertEqual('Fault repair work. Card replacement due to malfunction transmission system card. New try for cancelled PWIC45678.', result.action_and_reason)
        self.assertEqual('Santa Clara, CA, US', result.location)
        self.assertEqual('1 x 3 hours interruption', result.impact)
        self.assertEqual('noc@fiberprovider.com', result.email)
        self.assertEqual('8675309', result.phone)


if __name__ == '__main__':
    unittest.main()
