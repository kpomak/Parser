from app.core import Parser


def parse():
    parser = Parser()
    parser.parse_excel()
    parser.save_to_db()


if __name__ == "__main__":
    parse()
