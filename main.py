from grab.spider import Spider, Task

selectors = {
    'title': ['//title', ],
    'article': []
}

class SimpleSpider(Spider):

    def __init__(self, *args, **kwargs):
        self.initial_urls = kwargs.pop('urls')
        super(SimpleSpider, self).__init__(*args, **kwargs)

    def task_initial(self, grab, task):
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
            url_name_list = elem.select('//div[@class="b-text clearfix"]//p/a').selector_list
            url_link_list = elem.select('//div[@class="b-text clearfix"]//p/a/@href').selector_list
            maping_url = zip(url_name_list, url_link_list)
            article_element = elem._node.text_content()
            for name, link in maping_url:
                if name.text() in article_element:
                    name_index = article_element.index(name.text()) + len(name.text())
                    article_element = '{}[{}]{}'.format(article_element[:name_index], link.text(), article_element[name_index:])
            # FixMe Вынести в отдельный метод
            words = article_element.split()
            result = ''
            line = ''
            for word in words:
                if len(line) + len(word) < 80:
                    line += (' ' if line else '') + word
                else:
                    if line:
                        result += ''.join(['\n', line])
                    line = word
            if line:
                result += ''.join(['\n', line])
            print(result)


if __name__ == '__main__':
    urls = ['http://lenta.ru/news/2015/08/18/transgender_hired/', ]
    bot = SimpleSpider(urls=urls)
    bot.run()
    print(bot.render_stats())
