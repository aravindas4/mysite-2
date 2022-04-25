from sqlalchemy.orm import relationship
# from importlib_metadata import metadata
from sqlalchemy import create_engine, Column, MetaData, ForeignKey, literal



from clickhouse_sqlalchemy import Table, make_session


from clickhouse_sqlalchemy import Table, make_session, get_declarative_base, types, engines

uri = "clickhouse://default:@clickhouse_server/polls"

engine = create_engine(uri)
session = make_session(engine)
metadata = MetaData(bind=engine)


Base = get_declarative_base(metadata=metadata)

"""
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date publilshed')


    def __str__(self) -> str:
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
"""

class Question(Base):
    __tablename__ = "polls_question"

    id = Column("id", types.Int32, primary_key=True)
    question_text = Column("question_text", types.String)
    pub_date = Column(
        "pub_date", 
        types.DateTime,
        clickhouse_codec=('DoubleDelta', 'ZSTD'),
    )

    __table_args__ = (engines.Memory(),)


    
"""

class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.choice_text
"""

class Choice(Base):
    __tablename__ = "polls_choice"

    id = Column("id", types.Int32, primary_key=True)
    question_id = Column("question_id", types.Int32)

    choice_text = Column("choice_text", types.String)
    votes = Column("votes", types.Int32, server_default=literal(0))

    __table_args__ = (engines.Memory(),)
