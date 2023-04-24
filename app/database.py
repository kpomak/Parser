from datetime import date

from pony.orm import (
    Required,
    Database,
    Set,
    composite_index,
    set_sql_debug,
    db_session,
)

from app.conf import DEBUG


class Storage:
    db = Database()

    class Company(db.Entity):
        _table_ = "Сompanies"
        name = Required(str, unique=True)

        indicators = Set(lambda: Storage.Indicators)
        calculates = Set(lambda: Storage.Calculated)

    class Indicators(db.Entity):
        _table_ = "Product quantity"
        company = Required(lambda: Storage.Company)
        fact_qliq_1 = Required(int)
        fact_qliq_2 = Required(int)
        fact_qoil_1 = Required(int)
        fact_qoil_2 = Required(int)
        forecast_qliq_1 = Required(int)
        forecast_qliq_2 = Required(int)
        forecast_qoil_1 = Required(int)
        forecast_qoil_2 = Required(int)
        date = Required(date)

    class CalculatedIndicators(db.Entity):
        _table_ = "Calculated values"
        company = Required(lambda: Storage.Company)
        fact_qliq_sum = Required(int)
        fact_qoil_sum = Required(int)
        forecast_qliq_sum = Required(int)
        forecast_qoil_sum = Required(int)
        date = Required(date)
        composite_index(company, date)


    def __init__(self):
        self.db.bind(provider="sqlite", filename=f"../db.sqlite3", create_db=True)
        set_sql_debug(DEBUG)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def save_data(self, data_list: list[dict]):
        for data_item in data_list:
            company = self.Company.select(lambda comp: comp.name == data_item['company']).get()
            if not company:
                company = self.Company(name=data_item['company'])
                company.flush()

            data_item['company'] = company

            indicator = self.Indicators(**data_item)

    @db_session
    def calulate_sum(self):
        pass



if __name__ == '__main__':
    db = Storage()