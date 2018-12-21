#!/usr/bin/env python3

import psycopg2
from collections import OrderedDict as OrdDict


class ExitCommand:
    def __init__(self):
        self.message = 'Exit report.'
        self.keep_looping = False

    def execute(self):
        return 'Exiting report'


class QueryCommand:
    def __init__(self, message, query, formatter):
        self.message = message
        self.query = query
        self.formatter = formatter
        self.keep_looping = True

    def select_query(self):
        db = psycopg2.connect("dbname=news")

        cursor = db.cursor()
        cursor.execute(self.query)
        query_results = cursor.fetchall()

        db.close()

        return query_results

    def execute(self):
        try:
            query_result = self.select_query()
            return self.formatter(query_result)
        # I catch it here since here I know better what to do
        except psycopg2.Error as db_error:
            return format_error(db_error)


def format_heading_body(heading, body):
    return '[' + heading + ']' + '\n' + body


def format_error(db_error):
    return format_heading_body(
        'Problem with db',
        db_error.pgerror
    )


def format_most_popular_articles(articles):
    lines = [
        "\"{}\": {} views".format(title, count)
        for (title, count) in articles
    ]

    return format_heading_body(
        'Most Popular Articles',
        '\n'.join(lines)
    )


def format_most_popular_authors(authors):
    max_len = max([len(author_row[1]) for author_row in authors])
    row_format = "{:" + str(max_len) + "}: {} views"

    lines = [
        row_format.format(name, count)
        for (author_id, name, count) in authors
    ]

    return format_heading_body(
        'Most Popular Author',
        '\n'.join(lines)
    )


def format_day_with_most_errors(day_proportions):
    day = day_proportions[0][0]
    proportion = day_proportions[0][1]

    return format_heading_body(
        'Highest Error Rate Day',
        '{:%Y-%m-%d} with {:.2f} %'.format(day, proportion)
    )


def show_options(options):
    """
    Formats all the options

    :param options: program command dictionaries
    """
    print("[Log Report]")

    for i, option in enumerate(options, 1):
        print("[{}] {}".format(i, option.message))


def select_option(options):
    """
    Gets valid input from user. It checks if the entered option
    is a command key.

    :param options: the possible options the user can choose
    :returns: the chosen option dictionary
    """
    valid_inputs = range(1, len(options) + 1)
    selected_option = -1

    while selected_option not in valid_inputs:
        selected_option = input('Choose one of the valid options: ')

        try:
            selected_option = int(selected_option)
        except ValueError:
            print("Invalid input. Valid inputs are: " + str(valid_inputs))

    return options[selected_option - 1]


OPTIONS = [
    QueryCommand(
        'What are the most popular three articles of all time?',
        'SELECT title, visit_count FROM most_popular_articles LIMIT 3',
        format_most_popular_articles
    ),
    QueryCommand(
        'Who are the most popular article authors of all time?',
        'SELECT * FROM most_popular_authors',
        format_most_popular_authors
    ),
    QueryCommand(
        'On which days did more than 1% of requests lead to errors?',
        'SELECT * FROM error_proportion_per_day '
        'ORDER BY proportion DESC LIMIT 1',
        format_day_with_most_errors
    ),
    ExitCommand()
]


def main():
    keep_looping = True

    while keep_looping:
        print()
        show_options(OPTIONS)
        option = select_option(OPTIONS)
        option_result = option.execute()
        print()
        print(option_result)
        keep_looping = option.keep_looping


if __name__ == '__main__':
    main()
