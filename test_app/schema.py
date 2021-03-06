from django.db.models import Q

from django_graph_api.graphql.types import (
    Object,
    CharField,
    IntegerField,
    RelatedField,
    ManyRelatedField,
    Int,
    List,
    String,
)
from django_graph_api.graphql.schema import Schema

from .models import (
    Character as CharacterModel,
    Episode as EpisodeModel,
)


class Episode(Object):
    name = CharField(description='The name of an episode')
    number = IntegerField()
    characters = ManyRelatedField(
        'test_app.schema.Character',
        arguments={
            'types': List(String(null=False)),
        },
    )
    next = RelatedField('self')

    def get_next(self):
        return EpisodeModel.objects.filter(number=self.data.number + 1).first()

    def get_characters(self, types):
        q = Q()
        if types is not None:
            if 'human' not in types:
                q &= Q(human=None)
            if 'droid' not in types:
                q &= Q(droid=None)
        return self.data.characters.filter(q).order_by('pk')


class Character(Object):
    id = IntegerField(null=False)
    name = CharField()
    friends = ManyRelatedField('self')
    best_friend = RelatedField('self')
    appears_in = ManyRelatedField(Episode)

    def get_best_friend(self):
        return self.data.friends.order_by('pk').first()


class QueryRoot(Object):
    hero = RelatedField(Character, null=False)
    episodes = ManyRelatedField(Episode, arguments={'number': List(Int(null=False))})
    episode = RelatedField(Episode,
                           arguments={'number': Int(null=False)},
                           null=False
                           )

    def get_hero(self):
        return CharacterModel.objects.get(name='R2-D2')

    def get_episodes(self, number):
        episodes = EpisodeModel.objects.all()
        if number:
            episodes = episodes.filter(number__in=list(number))
        return episodes.order_by('number')

    def get_episode(self, number):
        return EpisodeModel.objects.get(number=number)


schema = Schema([QueryRoot])
