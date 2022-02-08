import os, sys, sqlite3, argparse
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


def setup_cli_args():
    parser = argparse.ArgumentParser(description="This is a CLI program storing contacts in an SQL database")
    parser.add_argument("--db", action="store", default="contact_book.db", help="Specifying database filepath. "
                                                                                "Default is cwd/contact_book.db")
    parser.add_argument("--add", action="store", default=[None], nargs='*', help="Adding a new contact, example usage: "
                                                                                 "'--add John Doe +441234567891'")
    parser.add_argument("--dl", action="store", default=[None], nargs='*', help="Deleting existing contact, example "
                                                                                "usage: '--dl John Doe +441234567891'")
    parser.add_argument("--vcard", nargs='?', const="contacts.vcf", help="Saving contacts to a specified .vcf file, "
                                                                         "if a filepath isn't specified the default "
                                                                         "is cwd/contacts.vcf")
    parser.add_argument("--list", action="store_true", default=False, help="Listing all contacts")

    return parser


def make_vcard(name, surname, phone_nr):
    return [
        "BEGIN:VCARD\n"
        "VERSION:2.1'\n"
        f"N:{surname};{name}\n"
        f"FN:{name} {surname}\n"
        f"TEL;WORK;VOICE:{phone_nr}\n"
        f"REV:1\n"
        "END:VCARD\n"
    ]


def write_vcard_to_file(f, vcard):
    with open(f, 'a') as f:
        f.writelines([line for line in vcard])


def create_vcard_contacts(filepath):
    sqliteConnection = None
    try:
        sqliteConnection = sqlite3.connect(DATA_BASE)
        cursor = sqliteConnection.cursor()
        for contact in cursor.execute("SELECT name, surname, phone_number FROM contacts").fetchall():
            vcard = make_vcard(contact[0], contact[1], contact[2])
            write_vcard_to_file(filepath, vcard)

        sqliteConnection.commit()
        cursor.close()
        print("Saved all contacts to " + filepath)
    except sqlite3.Error as error:
        print("Failed to list all contacts", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()


def parse_cli_args():
    global DATA_BASE
    parser = setup_cli_args()

    # Print help if no arguments are specified
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    # Checking for specified cli arguments and acting accordingly
    # Changing database filepath
    if args.db:
        DATA_BASE = args.db
    if not os.path.isfile(DATA_BASE):
        setup_database()

    # Adding a new contact
    if len(args.add) == 3:
        add_contact(args.add[0], args.add[1], args.add[2])
    # Deleting existing contact
    elif len(args.dl) == 3:
        del_contact(args.dl[0], args.dl[1], args.dl[2])
    # Saving contacts to .vcf file
    elif args.vcard:
        create_vcard_contacts(args.vcard)
    # Listing all contacts
    elif args.list:
        list_all_contacts()


def main():
    parse_cli_args()


if __name__ == "__main__":
    main()
