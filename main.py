from grab import Grab
from grab.spider import Spider, Task

# g = Grab()
# g.go('http://lenta.ru/news/2015/08/18/transgender_hired/')
# a = 1

selectors = {
    'title': ['//title', ],
    'article': []
}

class SimpleSpider(Spider):

    def __init__(self, *args, **kwargs):
        self.initial_urls = kwargs.pop('urls')
        super(SimpleSpider, self).__init__(*args, **kwargs)

    def task_initial(self, grab, task):
        # grab.doc.set_input('text', u'ночь')
        # grab.doc.submit(make_request=False)
        yield Task('parse', grab=grab)

    def task_parse(self, grab, task):
        #defaul 'title' or h1
        # Заголовок
        for elem in grab.doc.select('//h1[@class="b-topic__title"]'):
            print(elem._node.text_content())
        #default '//div/p' для получения ссылки '//div[@class="b-text clearfix"]//p/a/@href'
        # '//div[@class="b-text clearfix"]//p/a[@class="source"]/@href'
        # Текст
        for elem in grab.doc.select('//div[@class="b-text clearfix"]//p'):
            print(elem._node.text_content())
            # Можно внутри прямо переберать текущий элемент с использованием elem.select('//div[@class="b-text clearfix"]//p/a')
        # Ссылка
        for elem in grab.doc.select('//div[@class="b-text clearfix"]//p/a[@class="source"]/@href'):
            print(elem._node)
        # Текст в ссылке
        for elem in grab.doc.select('//div[@class="b-text clearfix"]//p/a[@class="source"]'):
            print(elem._node.text_content())


if __name__ == '__main__':
    urls = ['http://lenta.ru/news/2015/08/18/transgender_hired/', ]
    bot = SimpleSpider(urls=urls)
    bot.run()
    print(bot.render_stats())