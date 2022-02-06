import sqlite3
import os
import argparse
from tabulate import tabulate

DATA_BASE = "contact_book.db"


def perform_sql_query(action, query, *args):
    sqliteConnection = None
    result = {}
    try:
        sqliteConnection = sqlite3.connect(DATA_BASE)
        cursor = sqliteConnection.cursor()
        cursor.execute(query, args)
        sqliteConnection.commit()

        result["rowcount"] = cursor.rowcount
        result["selected_rows"] = len(cursor.fetchall())

        cursor.close()
    except sqlite3.Error as error:
        print(action + " failed", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
    return result


def setup_database():
    query = "CREATE TABLE contacts (name TEXT, surname TEXT, phone_number TEXT)"
    perform_sql_query("create a database", query)


def save_and_close_connection(con):
    con.commit()
    con.close()


def add_contact(name, surname, phone_nr):
    add_query = "INSERT INTO contacts VALUES (?, ?, ?)"
    search_query = "SELECT * FROM contacts WHERE name = ? AND surname = ? AND phone_number = ?"
    result = perform_sql_query("Looking for contact", search_query, name, surname, phone_nr)

    if result["selected_rows"] > 0:
        print("Contact already exists: {0} {1} {2}".format(name, surname, phone_nr))
    else:
        perform_sql_query("Adding a record to sql table", add_query, name, surname, phone_nr)
        print("Contact added successfully: {0} {1} {2}".format(name, surname, phone_nr))


def del_contact(name, surname, phone_nr):
    query = "DELETE FROM contacts WHERE name = ? AND surname = ? AND phone_number = ?"
    result = perform_sql_query("Deleting a record", query, name, surname, phone_nr)

    if result["rowcount"] > 0:
        print("Contact deleted successfully: {0} {1} {2}".format(name, surname, phone_nr))
    else:
        print("Contact doesn't exists: {0} {1} {2}".format(name, surname, phone_nr))


def list_all_contacts():
    sqliteConnection = None
    data = []
    try:
        sqliteConnection = sqlite3.connect(DATA_BASE)
        cursor = sqliteConnection.cursor()
        for contact in cursor.execute("SELECT name, surname, phone_number FROM contacts").fetchall():
            data.append([contact[0], contact[1], contact[2]])
        print(tabulate(data, headers=["Name", "Surname", "Phone Number"]))
        sqliteConnection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to list all contacts", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", action="store", default=[None], nargs='*', help="Adding a new contact, example usage: "
                                                                                 "'--add John Doe +440000000000'")
    parser.add_argument("--dl", action="store", default=[None], nargs='*', help="Deleting existing contact, example "
                                                                                "usage: '--dl John Doe +440000000000'")
    parser.add_argument("--list", action="store_true", default=False, help="Listing all contacts")
    args = parser.parse_args()

    if len(args.add) == 3:
        add_contact(args.add[0], args.add[1], args.add[2])
    elif len(args.dl) == 3:
        del_contact(args.dl[0], args.dl[1], args.dl[2])
    elif args.list:
        list_all_contacts()


def main():
    if not os.path.isfile(DATA_BASE):
        setup_database()
    parse_cli_args()


if __name__ == "__main__":
    main()