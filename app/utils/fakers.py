import factory

from django.contrib.auth import get_user_model

from app.users.models import Profile


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Faker('safe_email')
    password = factory.Faker('password')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    class Meta:
        model = get_user_model()


class UserProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    birth_place = factory.Faker('city')
    birth_date = factory.Faker('date')
    phone_number = factory.Faker('phone_number')
    is_guest = factory.Faker('boolean')

    class Meta:
        model = Profile