import sqlite3
from datetime import datetime

DATABASE = 'database.sqlite3'


def update_shift(person_id):
    """
    Add or update shift.
    :param person_id: ID of employee
    :return: True if new shift, else False
    :return: Current datetime
    """
    # Open connection to database
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM shifts WHERE PersonID = ' + person_id + '')

        rows = cur.fetchall()
        # If all attendance entries of this person have EndTime, create a new one
        new_shift = True
        for row in rows:
            if row[3] is None:
                new_shift = False
                current_shift_id = row[0]
                break

        # If new_shift is True, then attendee begins a new shift. Else, he/she ends the current one.
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if new_shift:  # Employee begins a new shift. Add new shift to database.
            command = "INSERT INTO shifts (PersonID, StartTime) " \
                      "VALUES ('{0}','{1}')".format(person_id, current_datetime)
            cur.execute(command)
        else:  # Employee ends an ongoing shift. Update shift's end time.
            command = "UPDATE shifts SET EndTime = '{0}' " \
                      "WHERE AttendanceID = {1}".format(current_datetime, current_shift_id)
            cur.execute(command)

        cur.execute('SELECT * FROM shifts WHERE PersonID = ' + person_id + '')

        return new_shift, current_datetime


def list_shift(person_id, show_last: int = 10):
    """
    List an employee's shift.
    :param person_id: Employee's ID
    :param show_last: Show last n number of shift
    :return: Array of recent shifts
    """
    assert show_last is not None
    assert show_last > 0

    # Open connection to database
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM shifts WHERE PersonID = '{0}' ORDER BY AttendanceID DESC".format(person_id))

        rows = cur.fetchall()

        return rows[:show_last]


def get_name(person_id):
    """
    Get employee's name.
    :param person_id: Employee's ID
    :return: Name
    """
    # Open connection to database
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT PersonName FROM persons WHERE PersonID = '{0}'".format(person_id))
        data = cur.fetchone()
        return data[0]


if __name__ == '__main__':
    print(get_name('17021357'))
