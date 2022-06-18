import graphene
from graphene_django.types import DjangoObjectType

from .models import Question, Choice


class ListMeta(graphene.Interface):
    limit = graphene.Int(required=True)
    offset = graphene.Int(required=True)
    count = graphene.Int(required=True)
    hasNext = graphene.Int(required=True)
    hasPrevious = graphene.Int(required=True)


class ListFilterType(graphene.Enum):
    BOOL = "bool"
    STRING = "string"
    INTEGER = "integer"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    RANGE = "range"

class ListFilter(graphene.ObjectType):
    field = graphene.String()
    value_for_display = graphene.String()
    data_type = graphene.Field(ListFilterType)

class SearchKeyword(graphene.ObjectType):
    key = graphene.String()
    value_for_display = graphene.String()


from django.db.models import CharField, Q
class BaseList(graphene.ObjectType):

    @classmethod
    def resolve(cls, root, info, *args, **kwargs):
        limit = kwargs.get('limit')
        offset = kwargs.get('offset')
        filters = kwargs.get('filters', [])
        other_filters = kwargs.get('other_filters', {})
        seachables = kwargs.get('seachables', [])

        field_model = cls.detail_type._meta.model

        final_filters = {}
        if filters is not None:
            for _filter in filters:
                field_type = field_model._meta.get_field(_filter["field"])

                if isinstance(field_type, CharField):
                    final_filters[_filter["field"] + "__icontains"] = _filter["value"]
                else:
                    final_filters.update[
                        _filter["field"]: _filter["value"]
                    ]

        seach_qs = Q()

        if seachables is not None:
            for seachable in seachables:
                if seachable["key"] == "default":
                    for field in cls.search_key_field_map[seachable["key"]]:
                        seach_qs.add(Q(**{field: seachable["value"]}), Q.OR)

        qs = cls.get_queryset().filter(**final_filters, **other_filters).filter(
            seach_qs
        ).distinct()
        count = qs.count()
        objects = qs[offset: limit+offset]
        obj = cls(limit=limit, offset=offset, objects=objects, count=count)
        obj.hasNext = limit + offset < count
        obj.hasPrevious = offset > 0
        return obj

    @classmethod
    def get_queryset(cls):
        class_model = cls.detail_type._meta.model
        return class_model.objects.all()


from graphql import GraphQLError

class DetailMixin:
    lookup_field = "pk"

    @classmethod
    def resolve(cls, *args, **kwargs):
        filters = {}
        filters[cls.lookup_field] = kwargs["id"]

        try:
            obj = cls._meta.model.objects.filter(**filters).get()
        except cls._meta.model.DoesNotExist:
            raise GraphQLError("Object Does Not Exist")

        return obj



class ChoiceType(DetailMixin, DjangoObjectType):
    class Meta:
        model = Choice
        fields = ("id", "choice_text", "votes", "question")


class ChoiceList(BaseList):
    detail_type = ChoiceType

    objects = graphene.List(detail_type, required=True)

    class Meta:
        interfaces = (ListMeta,)
    
    # @classmethod
    # def resolve(cls, info, *args, **kwargs):
    #     return super().resolve(info, *args, **kwargs)
    


class QuestionType(DetailMixin, DjangoObjectType):
    paginated_choices = graphene.Field(
        'polls.types.ChoiceList',
        limit=graphene.Argument(graphene.Int, default_value=10),
        offset=graphene.Argument(graphene.Int, default_value=0),
    )

    choices = graphene.List(ChoiceType)

    class Meta:
        model = Question
        only_fields = ("id", "question_text", "pub_date", "choices")

    def resolve_choices(self, info, *args, **kwargs):
        return self.choices.all()
    
    def resolve_paginated_choices(self, info, *args, **kwargs):
        filters = kwargs.get('other_filters', {})
        filters.update({"question_id": self.pk})
        kwargs["other_filters"] = filters
        return ChoiceList.resolve(ChoiceList, info, *args, **kwargs)

class QuestionList(BaseList):
    detail_type = QuestionType

    objects = graphene.List(detail_type, required=True)
    filters = graphene.List(ListFilter)
    seachables = graphene.List(SearchKeyword)

    filter_options = [
        ListFilter(
            field="question_text", 
            value_for_display="Question", 
            data_type=ListFilterType.STRING
        ),
        ListFilter(
            field="pub_date",
            value_for_display="Published On",
            data_type=ListFilterType.DATETIME
        )
    ]

    search_key_field_map = {
        "default": ["question_text__icontains"]
    }

    search_options = [
        SearchKeyword(
            key="default",
            value_for_display="Default"
        )
    ]

    class Meta:
        interfaces = (ListMeta,)
    
    def resolve_seachables(self, info, *args, **kwargs):
        return self.search_options

    def resolve_filters(self, info, *args, **kwargs):
        return self.filter_options



class VoteQuestionInput(graphene.InputObjectType):
    question_id = graphene.ID(required=True)
    choice_id = graphene.ID(required=True)


class VoteQuestion(graphene.Mutation):
    class Arguments:
        input = VoteQuestionInput(required=True)

    question = graphene.Field(QuestionType)

    @classmethod
    def mutate(cls, root, info, input):
        question = Question.objects.get(pk=input.question_id)
        choice = question.choices.all().get(pk=input.choice_id)
        choice.votes += 1
        choice.save()

        return VoteQuestion(question=question)
