from openpyxl import load_workbook
from datetime import date
from sys import argv

from app.conf import *
from app.database import Storage


class ExcelParser:
    def __init__(self):
        self.data = []

    def parse_excel(self):
        try:
            file_name = 'file.xlsx' ############# argv[1]
            workbook = load_workbook(file_name)
        except FileNotFoundError:
            print('Файл не найден.')
            exit(1)
        except Exception:
            print('Произошла ошибка')
            exit(1)

        worksheet = workbook.active
        worksheet = worksheet[TABLE_HEADER:worksheet.max_row]

        day_of_month = (date(2023, 1, day) for day in range(1, 32))
        for row in worksheet:
            item = {
                'company': row[COMPANY].value,
                'fact_qliq_1': row[FACT_QLIQ_1].value,
                'fact_qliq_2': row[FACT_QLIQ_2].value,
                'fact_qoil_1': row[FACT_QOIL_1].value,
                'fact_qoil_2': row[FACT_QOIL_2].value,
                'forecast_qliq_1': row[FORECAST_QLIQ_1].value,
                'forecast_qliq_2': row[FORECAST_QLIQ_2].value,
                'forecast_qoil_1': row[FORECAST_QOIL_1].value,
                'forecast_qoil_2': row[FORECAST_QOIL_2].value,
                'date': next(day_of_month),
            }
            self.data.append(item)


class Parser(ExcelParser):
    def __init__(self):
        super().__init__()
        self.db = Storage()

    def parse_excel(self):
        super().parse_excel()
        self.db.save_data(self.data)



if __name__ == "__main__":
    file = Parser()
    file.parse_excel()
