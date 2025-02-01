import factory
from factory import fuzzy
from django.contrib.auth import get_user_model

from api.track.models import Venue, Track
from api.users.models import Profile


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
    gender = fuzzy.FuzzyChoice([x[0] for x in Profile.Gender.choices])
    occupation  = factory.Faker('job')
    marital_status = fuzzy.FuzzyChoice([x[0] for x in Profile.MaritalStatus.choices])

    class Meta:
        model = Profile


class VenueFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    location = factory.Faker('city')
    description = factory.Faker('text')
    is_available = True

    class Meta:
        model = Venue


class TrackFactory(factory.django.DjangoModelFactory):
    venue = factory.SubFactory(VenueFactory)
    name = factory.Faker('name')
    description = factory.Faker('text')
    is_available = True
    capacity = factory.Faker('random_int', min=1, max=100)

    class Meta:
        model = Track