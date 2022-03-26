import sqlite3

from flask import Flask, request


def create_app():
    app = Flask(__name__)

    def get_db():
        """
        Helper to get the database for application

        :return: database for use with api
        """
        return sqlite3.connect("database.db")

    @app.route('/operators', methods=['GET'])
    def get_operators():
        """
        Returns a list of all operators for a given company.

        :return: list of all operators associated with a given company
        """
        db = get_db()
        cursor = db.cursor()
        company = request.args.get('company')
        limit = request.args.get('limit') or 10000
        offset = request.args.get('offset') or 0
        if not company:
            return {'data': "Please provide a company"}, 400

        sql = """
        SELECT nm_socio
        FROM BRAZIL
        WHERE nm_fantasia = ?
        LIMIT ?
        OFFSET ?
        """
        cursor = cursor.execute(sql, [company, limit, offset])
        response = {
            'data': [doc[0] for doc in cursor]
        }
        cursor.close()
        return response, 200

    @app.route('/companies', methods=['GET'])
    def get_companies():
        """
        Returns a list of all companies that corresponds to provided input
        If company: All companies connected to a given company via shared operators
        If operator: All companies associated with a given operator

        :return: list of all companies associated with a given input
        """
        db = get_db()
        cursor = db.cursor()
        operator = request.args.get('operator')
        company = request.args.get('company')
        limit = request.args.get('limit') or 10000
        offset = request.args.get('offset') or 0
        if not operator and not company:
            return {'data': "Please provide a company or an operator"}, 400
        if operator and company:
            return {'data': "Please provide a company or operator, not both"}, 400

        if operator:
            sql = """
            SELECT nm_fantasia
            FROM BRAZIL
            WHERE nm_socio = ?
            LIMIT ?
            OFFSET ?
            """
            cursor = cursor.execute(sql, [operator, limit, offset])
        elif company:
            sql = """
            WITH CTE as (
                SELECT nm_socio
                FROM BRAZIL
                where nm_fantasia = ?
            )
            SELECT DISTINCT nm_fantasia
            FROM BRAZIL
            INNER JOIN CTE ON BRAZIL.nm_socio = CTE.nm_socio
            LIMIT ?
            OFFSET ?
            """
            cursor = cursor.execute(sql, [company, limit, offset])
        response = {
            'data': [doc[0] for doc in cursor]
        }
        cursor.close()
        return response, 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
