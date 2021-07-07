from basescript import BaseScript

from application import create_app


class BookStore(BaseScript):
    def __init__(self):
        super(BookStore, self).__init__()
        self.app = create_app()

    def run(self):
        self.log.info("Start of the Book Store Program")
        self.app.run(debug=True)
        self.log.info("End of the  Book Store Program")


if __name__ == '__main__':
    BookStore().start()
