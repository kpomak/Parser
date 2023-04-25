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
    """
    Класс описывает таблицы и методы базы данных.
    """
    db = Database()

    class Company(db.Entity):
        """
        Таблица компаний.
        """
        _table_ = "Сompanies"
        name = Required(str, unique=True)

        indicators = Set(lambda: Storage.Indicators)
        calculates = Set(lambda: Storage.Calculated)

    class Indicators(db.Entity):
        """
        Таблица показателей продукции/производства.
        """
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

    class Calculated(db.Entity):
        """
        Таблица рассчетных значений.
        """
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
        """
        Метод заполняет таблицу показателей на основании данных из data_list,
        если компании еще нет в таблице компаний, то создает новую запись.
        """
        for data_item in data_list:
            company = self.Company.select(
                lambda comp: comp.name == data_item["company"]
            ).get()
            if not company:
                company = self.Company(name=data_item["company"])
                company.flush()

            data_item["company"] = company

            indicator = self.Indicators(**data_item)

    @db_session
    def calculate_sum(self):
        """
        Метод рассчитывает суммарные показатели каждой компании,
        сгруппированные по дате, если в одну дату у компании было
        несколько фактических и прогнозируемых значений, например,
        у разных филиалов       
        """
        # проходим по всем записям в таблице показатели
        data = self.Indicators.select()
        for line in data:

            # получаем запись из таблицы рассчетные показатели за определенную дату
            # определенной компании
            calculated_sum = self.Calculated.select(
                lambda record: record.company == line.company
                and record.date == line.date
            ).get()

            # если такой записи нет - создаем
            if not calculated_sum:
                calculated = self.Calculated(
                    company=line.company,
                    fact_qliq_sum=line.fact_qliq_1 + line.fact_qliq_2,
                    fact_qoil_sum=line.fact_qoil_1 + line.fact_qoil_2,
                    forecast_qliq_sum=line.forecast_qliq_1 + line.forecast_qliq_2,
                    forecast_qoil_sum=line.forecast_qoil_1 + line.forecast_qoil_2,
                    date=line.date,
                )
                calculated.flush()

            # если уже есть запись, добавляем значения
            # в этот момент я подумал, что неправильно понял задание,
            # похоже надо было складывать по компаниям
            else:
                calculated.fact_qliq_sum += (line.fact_qliq_1 + line.fact_qliq_2)
                calculated.fact_qoil_sum += (line.fact_qoil_1 + line.fact_qoil_2)
                calculated.forecast_qliq_sum += (
                    line.forecast_qliq_1 + line.forecast_qliq_2
                )
                calculated.forecast_qoil_sum += (
                    line.forecast_qoil_1 + line.forecast_qoil_2
                )


if __name__ == "__main__":
    db = Storage()
