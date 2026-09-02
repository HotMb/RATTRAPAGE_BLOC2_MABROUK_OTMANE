from django.test import TestCase
from planning.models import User


class UserRoleTests(TestCase):
    def test_user_has_role_field_with_expected_choices(self):
        user = User.objects.create_user(
            username='alice', password='pass1234', role=User.Role.ADMIN
        )
        self.assertEqual(user.role, 'ADMIN')
        self.assertIn(('ADMIN', 'Administrateur'), User.Role.choices)
        self.assertIn(('INTERVENANT', 'Intervenant'), User.Role.choices)
        self.assertIn(('ETUDIANT', 'Étudiant'), User.Role.choices)
