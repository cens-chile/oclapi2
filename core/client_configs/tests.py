from django.core.exceptions import ValidationError

from core.client_configs.models import ClientConfig
from core.common.tests import OCLTestCase
from core.orgs.tests.factories import OrganizationFactory


class ClientConfigTest(OCLTestCase):
    def test_is_home(self):
        self.assertTrue(ClientConfig().is_home)
        self.assertTrue(ClientConfig(type='home').is_home)
        self.assertFalse(ClientConfig(type='blah').is_home)

    def test_home_config_validation(self):
        client_config = ClientConfig(config=dict())

        with self.assertRaises(ValidationError) as ex:
            client_config.full_clean()

        self.assertEqual(
            ex.exception.message_dict,
            dict(
                config=['This field cannot be blank.'],
                resource_type=['This field cannot be null.'],
                resource_id=['This field cannot be null.'],
                tabs=['At least one tab config is mandatory.'],
            )
        )

        org = OrganizationFactory()
        client_config.resource = org
        client_config.config = dict(foo='bar')

        with self.assertRaises(ValidationError) as ex:
            client_config.full_clean()

        self.assertEqual(ex.exception.message_dict, dict(tabs=['At least one tab config is mandatory.']))

        client_config.config = dict(tabs='foobar')

        with self.assertRaises(ValidationError) as ex:
            client_config.full_clean()

        self.assertEqual(ex.exception.message_dict, dict(tabs=['Tabs config must be a list.']))

        client_config.config = dict(tabs=['foobar'])

        with self.assertRaises(ValidationError) as ex:
            client_config.full_clean()

        self.assertEqual(ex.exception.message_dict, dict(tabs=['Invalid Tabs config.']))

        client_config.config = dict(tabs=[dict(foo='bar')])

        with self.assertRaises(ValidationError) as ex:
            client_config.full_clean()

        self.assertEqual(ex.exception.message_dict, dict(tabs=['Exactly one of the Tabs must be default.']))

        client_config.config = dict(tabs=[dict(foo='bar', default=True), dict(foo='bar', default=True)])

        with self.assertRaises(ValidationError) as ex:
            client_config.full_clean()

        self.assertEqual(ex.exception.message_dict, dict(tabs=['Exactly one of the Tabs must be default.']))

        client_config.config = dict(tabs=[dict(foo='bar', default=True), dict(foo='bar', default=False)])
        client_config.full_clean()
