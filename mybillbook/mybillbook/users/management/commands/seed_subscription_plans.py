from django.core.management.base import BaseCommand
from users.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Seeds the database with subscription plans'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Free Trial',
                'price': 0,
                'duration': 14,
                'features': [
                    'Basic features',
                    'Limited access',
                    '14 days trial period'
                ],
                'is_trial': True
            },
            {
                'name': 'Basic Monthly',
                'price': 999,
                'duration': 30,
                'features': [
                    'All basic features',
                    'Unlimited access',
                    'Email support',
                    'Basic analytics'
                ],
                'is_trial': False
            },
            {
                'name': 'Pro Monthly',
                'price': 1999,
                'duration': 30,
                'features': [
                    'All Basic features',
                    'Priority support',
                    'Advanced analytics',
                    'Custom reports',
                    'API access'
                ],
                'is_trial': False
            },
            {
                'name': 'Basic Yearly',
                'price': 9990,
                'duration': 365,
                'features': [
                    'All basic features',
                    'Unlimited access',
                    'Email support',
                    'Basic analytics',
                    '2 months free'
                ],
                'is_trial': False
            },
            {
                'name': 'Pro Yearly',
                'price': 19990,
                'duration': 365,
                'features': [
                    'All Pro features',
                    'Priority support',
                    'Advanced analytics',
                    'Custom reports',
                    'API access',
                    '2 months free'
                ],
                'is_trial': False
            },
            {
                'name': 'Enterprise',
                'price': 49990,
                'duration': 365,
                'features': [
                    'All Pro features',
                    'Dedicated support',
                    'Custom integrations',
                    'Advanced security',
                    'SLA guarantee',
                    '3 months free'
                ],
                'is_trial': False
            }
        ]

        for plan_data in plans:
            SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'price': plan_data['price'],
                    'duration': plan_data['duration'],
                    'features': plan_data['features'],
                    'is_trial': plan_data['is_trial']
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded subscription plans')) 