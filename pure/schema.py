from email.policy import default
from graphene import ObjectType, String, Field, Int
import graphene


class Episode(graphene.Enum):
    NEWHOPE = 1
    EMPIRE = 2
    JEDI = 3



class Person(ObjectType):
    full_name = String(required=True)
    first_name = String()
    last_name = String()
    constant = Episode()

    class Meta:
        name = "Personsgasgdgd"

    def resolve_full_name(parent, info, **kwargs):
        print("resolvin fn")
        print(parent)
        print(type(parent))
        print(parent.__dict__)
        return f"{parent.first_name} {parent.last_name}"

    @classmethod
    def resolve(cls, info, *args, **kwargs):
        print("Person******")
        print(info)
        print(args[0])
        print(dir(args[0]))
        print(args[0].variable_values)
        print(kwargs)
        return cls(
            first_name="Aravinda", 
            last_name="Holla",
            constant=Episode.JEDI
        )



class Query(ObjectType):
    hello1 = Field(String, name=String(default_value=10))
    hello = String(name=String(default_value="stranger"))
    goodbye = String()
    me = Field(Person, resolver=Person.resolve, some=graphene.Argument(
        Episode
    ))

    def resolve_hello1(root, info, name):
        return f"Hello {name}"

    def resolve_goodbye(parent, info):
        print(parent)
        print(type(parent))
        print(hasattr(parent, "hello"))
        return f"See ya!"
