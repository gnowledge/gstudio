from HTMLParser import HTMLParser
import urllib 

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    pg_content = ''
    pg_name = ''
    flag1 = 0
    flag2 = 0
    def handle_starttag(self, tag, attrs):
        if(('name', 'pg_name') in attrs):
            self.flag1 = 1
        if(('name', 'pg_content') in attrs):
            self.flag2 = 1
        
    def handle_endtag(self, tag):
        a = 0       
    
    def handle_data(self, data):
        if(self.flag1 == 1):
            self.pg_name = data
            self.flag1 = 0
        if(self.flag2 == 1):
            self.pg_content = data
            self.flag2 = 0

    def return_values(self):
        return self.pg_name ,self.pg_content

def get_content(html_body):
    parser = MyHTMLParser()
    parser.feed(html_body)
    pg_name , pg_content = parser.return_values()
    pg_content = pg_content.strip()
    pg_name = pg_name.strip()
    return pg_name,pg_content
