import graphene
from graphene_django.types import DjangoObjectType

from .models import Question, Choice


class QuestionType(DjangoObjectType):
    class Meta:
        model = Question
        fields = ("id", "question_text", "pub_date", "choices")


class ChoiceType(DjangoObjectType):
    class Meta:
        model = Choice
        fields = ("id", "choice_text", "votes", "question")


class VoteQuestionInput(graphene.InputObjectType):
    question_id = graphene.ID()
    choice_id = graphene.ID()


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




