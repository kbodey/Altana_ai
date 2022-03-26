import argparse
import csv
import os
import sqlite3


class Database:

    def __init__(self, file_name, database_name):
        """
        Constructor for creating a database for Brazilian app

        :param file_name: Name of the input file used to create the database
        :param database_name: Name of the output file or database file
        """
        self.file_name = file_name
        if database_name.endswith('.db'):
            self.database_name = database_name
        else:
            self.database_name = '{}.db'.format(database_name)

        print('Creating database file:', self.database_name)
        print('Using', self.file_name, 'as input to the database')

    def create_database(self):
        """
        Creates a database file using data supplied by the user.

        :return: None, but creates a .db file
        """
        connection = sqlite3.connect(self.database_name)
        cursor = connection.cursor()
        cursor.execute('''DROP TABLE IF EXISTS BRAZIL''')

        with open(self.file_name, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            # First get the headers from the reader and throw them away because they are well defined already
            for header in reader:
                break
            cursor.execute('''
                CREATE TABLE BRAZIL
                (
                    nr_cnpj                 TEXT,
                    nm_fantasia             TEXT,
                    sg_uf                   TEXT,
                    in_cpf_cnpj             INTEGER,
                    nr_cpf_cpnj_socio       TEXT,
                    cd_qualificacao_socio   INTEGER,
                    ds_qualificacao_socio   TEXT,
                    nm_socio                TEXT
                );'''
                           )

            for row in reader:
                cursor.execute("""
                    INSERT INTO BRAZIL (nr_cnpj,nm_fantasia,sg_uf,in_cpf_cnpj,nr_cpf_cpnj_socio,cd_qualificacao_socio,ds_qualificacao_socio,nm_socio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                               row
                               )

            cursor.execute("""
                CREATE INDEX "company_index" ON "BRAZIL" (
                    "nm_fantasia"
                );"""
                           )
            cursor.execute("""
                CREATE INDEX "operator_index" ON "BRAZIL" (
                    "nm_socio"
                );"""
                           )

        connection.commit()
        connection.close()

    def move_database_file(self):
        """
        Moves newly created database file to proper place for api usage

        :return: None
        """
        new_location = "../brazilian-api/{}".format(self.database_name)
        print('Moving', self.database_name, 'to', new_location)
        os.replace(self.database_name, new_location)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="List fish in aquarium.")
    parser.add_argument("-d", "--database", help='Database output file name')
    parser.add_argument("-f", "--file_name", help='Location or name of the input file')
    args = parser.parse_args()

    database = args.database or 'database.db'
    the_file_name = args.file_name or 'ReceitaFederal_QuadroSocietario.csv'
    db = Database(file_name=the_file_name, database_name=database)
    db.create_database()
    db.move_database_file()
