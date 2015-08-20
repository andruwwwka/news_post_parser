import re
import os
from grab.spider import Spider, Task

url_pattern = r'^(?:http|ftp)s?://(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' \
              r'localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+)$'

max_items_in_string = 80

default_selectors_config = {
    'default': {
        'title': '//title', #gazeta //h1[@class="b-topic__title"]
        'text': '//div//p', #gazeta //div[@class="b-text clearfix"]//p
        'link_text': '/a', #gazeta //div[@class="b-text clearfix"]//p/a
        'link': '/@href', #gazeta //div[@class="b-text clearfix"]//p/a/@href
    }
}

class RegexValidator(object):
    _pattern = ''

    def __init__(self, pattern=''):
        self.pattern = pattern
        self._regex = re.compile(self.pattern, re.IGNORECASE)

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, new_patern):
        if self.pattern != new_patern:
            self._pattern = new_patern
            self._regex = re.compile(self.pattern, re.IGNORECASE)


class UrlValidator(RegexValidator):

    def __init__(self, pattern=''):
        super(UrlValidator, self).__init__(
            pattern or url_pattern
        )

    def is_valid(self, url=''):
        return bool(re.match(self._regex, url))

class FileWriter(object):

    def __init__(self, url):
        # FixMe наверное надо создавать директории
        filedir = '{}/{}'.format(os.path.abspath(os.curdir), url[url.index('://')+3:])
        if filedir[-1] == '/':
            filedir = filedir[:-1]
        file_path = filedir[:filedir.rindex('/')]
        os.makedirs(file_path)
        file_name = filedir.split('/')[-1].split('.')[0]
        self.file = open('{}/{}'.format(file_path, file_name), 'w')

    def write(self, value):
        self.file.write('{}{}'.format(value, '\n'))

    def close_thread(self):
        self.file.close()

class SimpleSpider(Spider):

    def __init__(self, *args, **kwargs):
        self.initial_urls = kwargs.pop('urls')
        self.selectors_config = kwargs.pop('selectors_config')
        self.url_validator = UrlValidator()
        super(SimpleSpider, self).__init__(*args, **kwargs)

    def start_task_generator(self):
        """
        Process `self.initial_urls` list and `self.task_generator`
        method.  Generate first portion of tasks.
        """

        if self.initial_urls:
            for url in self.initial_urls:
                if not self.url_validator.is_valid(url):
                    print('Could not resolve relative URL because url [{}] is not valid.\n'.format(url))
                    continue
                self.add_task(Task('initial', url=url))

        self.task_generator_object = self.task_generator()
        self.task_generator_enabled = True
        # Initial call to task generator before spider has started working
        self.process_task_generator()

    def task_initial(self, grab, task):
        yield Task('parse', grab=grab)

    def task_parse(self, grab, task):
        # Заголовок
        #FixMe Добавить ниже валидацию конфигурации
        writer = FileWriter(task.url)
        settings_template = self.selectors_config.get(task.url) if task.url in self.selectors_config \
            else default_selectors_config.get('default')
        head_tag = settings_template.get('title')
        for elem in grab.doc.select(head_tag):
            writer.write(elem._node.text_content())
        # Текст
        xpath_param_text = settings_template.get('text')
        xpath_param_link_text = '{}{}'.format(xpath_param_text, settings_template.get('link_text'))
        xpath_param_link = '{}{}'.format(xpath_param_link_text, settings_template.get('link'))
        for elem in grab.doc.select(xpath_param_text):
            url_name_list = elem.select(xpath_param_link_text).selector_list
            url_link_list = elem.select(xpath_param_link).selector_list
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
                if len(line) + len(word) < max_items_in_string:
                    line += (' ' if line else '') + word
                else:
                    if line:
                        result += '{}{}'.format('\n', line)
                    line = word
            if line:
                result += '{}{}'.format('\n', line)
            writer.write(result)
        writer.close_thread()


if __name__ == '__main__':
    urls = ['http://lenta.ru/news/2015/08/18/transgender_hired/', 'http://news.rambler.ru/science/31092820/']
    selectors_config = default_selectors_config
    bot = SimpleSpider(urls=urls, selectors_config=selectors_config)
    bot.run()
    print(bot.render_stats())
