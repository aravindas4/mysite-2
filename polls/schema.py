import graphene

from .models import Question
from .types import QuestionType, ChoiceType, VoteQuestion,QuestionList, ListFilter
# from graphene_django import DjangoListField




class ListFilterArgument(graphene.InputObjectType):
    field = graphene.String(required=True)
    value = graphene.String(required=True)


class SearchKeywordArgument(graphene.InputObjectType):
    key = graphene.String(required=True)
    value = graphene.String(required=True)


class SortOrder(graphene.Enum):
    ASC = "ASC"
    DESC = "DESC"

class SortInput(graphene.InputObjectType):
    field = graphene.String(required=True)
    order = graphene.Field(SortOrder, required=True)

class Query(graphene.ObjectType):
    question = graphene.Field(
        QuestionType,
        id=graphene.Argument(graphene.ID),
        resolver=QuestionType.resolve
    )
    # choices = graphene.List(ChoiceType)
    # choice = graphene.Field(ChoiceType, choice_id=graphene.ID())
    questions = graphene.Field(
        QuestionList,
        resolver=QuestionList.resolve,
        limit=graphene.Argument(graphene.Int, default_value=10),
        offset=graphene.Argument(graphene.Int, default_value=0),
        filters=graphene.List(ListFilterArgument, default_value=[]),
        seachables=graphene.List(SearchKeywordArgument, default_value=None),
        sort=graphene.Argument(SortInput, default_value=None)
    )

    # def resolve_question(self, info, question_id):
    #     return Question.objects.get(pk=question_id)

    def resolve_choices(self, info, **kwargs):
        return ChoiceType.objects.all()

    def resolve_choice(self, info, choice_id):
        return ChoiceType.objects.get(pk=choice_id)

    # def resolve(self, next, root, info, **args):
    #     # import ipdb; ipdb.set_trace()
    #     print(args)
    #     # print(kwargs)
    #     print("SOMMMMMMM")
    #     # modify the qs for pagination
    #     # individual resolvers
    #     pass


class Mutation(graphene.ObjectType):
    vote_question = VoteQuestion.Field()
