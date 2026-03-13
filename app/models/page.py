class Page:

    def __init__(self, url):

        self.url = url
        self.status = None

        self.title = None
        self.description = None
        self.h1 = None

        self.in_links = set()
        self.out_links = set()