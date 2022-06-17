from datetime import datetime

from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, analyzer, connections

connections.create_connection(hosts=["localhost"])


class Article(Document):
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    body = Text(analyzer='snowball')
    tags = Keyword()
    published_from = Date()
    lines = Integer()

    class Index:
        name = 'blog'
        settings = {
            "number_of_shards": 2
        }

    def save(self, **kwargs):
        self.lines = len(self.body.split())
        return super().save(**kwargs)


    def is_published(self):
        return datetime.now() > self.published_from


# Article.init()


# article = Article(meta={'id': 42}, title='Hello world!', tags=['test'])
# article.body = ''' looong text'''
# article.published_from = datetime.now()
# article.save()

# article = Article.get(id=42)
# print(article.is_published())

# print(connections.get_connection().cluster.health())