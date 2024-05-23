#
# Copyright (C) 2022 Vaticle
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from typedb.driver import TypeDB, SessionType, TransactionType, TypeDBOptions
from enum import Enum
import argparse
import config

# Verbosity option implementation
parser = argparse.ArgumentParser(description="Bookstore example requests")
parser.add_argument("-v", "--verbose", "-d", "--debug", help="Increase output verbosity",
                    dest="verbose", action="store_true")
args = vars(parser.parse_args())

if args["verbose"]:  # if the argument was set
    print("High verbosity option turned on.")
    debug = True  # Shows verbose debug messages in the console output
else:
    debug = False  # No debug messages


class ResultCode(Enum):
    OK = 0,
    INPUT_INVALID = 1,
    EXIT = 2


def selection(driver):  # This is the main UI to select a function to proceed with

    print("Please choose one of the following functions: ")
    print("1. Search for a book")
    print("2. Search for a user")
    print("3. Search for an order")
    print("4. Search for books by genre")
    print("0. Exit")
    selection = input("Your request: ")  # Storing answer here
    if selection == "":
        print("Empty selection recognized. Please try again.")
        return ResultCode.INPUT_INVALID
    elif selection == "1":  # We chose variant #1 — searching for a book
        return search_book(input("Searching for a book. Please type in an ISBN or press enter for a full listing: "), driver)
    elif selection == "2":  # 2. Searching for a user
        return search_user(input("Searching for a user. Please type in a foreign ID or press enter for a full listing: "), driver)
    elif selection == "3":  # 3. Searching for an order
        return search_order(input("Searching for an order. Please type in an order ID or press enter for a full listing: "), driver)
    elif selection == "4":  # 4. Searching for books by genre
        show_all_genres(driver)  # Display all genres as a tip
        return search_genre(input("Searching for books by genre. Please type in genre name: "), driver)
    elif selection == "0" or "exit" or "exit()" or "close" or "close()" or "help":  # Exit the program
        return ResultCode.EXIT
    else:
        print("Invalid selection recognized. Please try again.")  # Something else / unrecognized - repeat
        return ResultCode.INPUT_INVALID


def search_book(ISBN, driver):  # Search book by ISBN (or show all books if empty ISBN given)

    if ISBN == "":  # empty ISBN given
        print("Empty input. Listing all books")  
        return show_all_books(driver)  # Display all books
    else:  # Non-empty ISBN given
        return show_book(ISBN, driver)  # Display selected book


def show_book(ISBN, driver):  # Searching book by ISBN and print info
    result = []
    with driver.session(config.db, SessionType.DATA) as session:  # Access data in the database
        with session.transaction(TransactionType.READ) as transaction:  # Open transaction to read
            typeql_read_query = "match $b isa book, has ISBN '" + ISBN + "', has name $n, " \
                                "has book-author $ba; " \
                                "get $n, $ba;"
            if debug: print("Executing TypeQL read Query: " + typeql_read_query)
            iterator = transaction.query.get(typeql_read_query)  # Execute match query
            k = 0  # Counter initialisation
            for item in iterator:  # Iterating through results of the match query
                print(ISBN, item.get("n").get_value(), item.get("ba").get_value(), sep=" — ")  # Print every result
                k += 1
    print("Books found:", k)  # Print the counter as the number of results found
    result.append(k)

    # Rating computation
    with driver.session(config.db, SessionType.DATA) as session:  # Access data in the database
        with session.transaction(TransactionType.READ) as transaction:  # Open transaction to read
            typeql_read_query = "match $b isa book, has ISBN '" + ISBN + "';" \
                                "$r (product: $b, author:$a) isa review; $r has rating $rating;" \
                                "get $rating;"
            if debug: print("Executing TypeQL read Query: " + typeql_read_query)
            iterator = transaction.query.get(typeql_read_query)  # Execute match query
            g = 0  # Initialising counter
            s = 0  # Initialising sum variable
            for item in iterator:  # Iterating through query results
                g += 1  # Increase the counter for every query result
                rating = item.get("rating").get_value()  # Get rating value
                if debug: print(g, "Review rating found:", rating)
                s = s + rating  # Add to sum
            if g > 0:  # If there was any rating (counter was increased)
                average = round(s/g, 2)
                print("Total rating records:", str(g) + ". Average book rating:", average)
                # printed average (s (sum) divided by g (number of results)), rounded to 2 signs after a comma
                result.append(average)
            else:  # No rating results found by the query
                print("No rating data for this book.")
                result.append(False)
    return result


def search_user(user, driver):  # Search user by foreign-id (or show all users if empty id given)

    if user == "":
        print("Empty input. Listing all users")
        return show_all_users(driver)  # Display all users
    else:
        return show_user(user, driver)  # Display selected user


def show_user(user, driver):  # Display user by foreign-id
    result = []
    with driver.session(config.db, SessionType.DATA) as session:  # Access data in the database
        with session.transaction(TransactionType.READ) as transaction:  # Open transaction to read
            typeql_read_query = "match $u isa user, has id $i, has name $n, has foreign-id '" + user + "'; " \
                                "get $i, $n;"
            if debug: print("Executing TypeQL read Query: " + typeql_read_query)
            iterator = transaction.query.get(typeql_read_query)  # Executing query
            k = 0
            for item in iterator:  # Iterating through results
                print(user, item.get("n").get_value(), item.get("i").get_value(), sep=" — ")  # Print results
                k += 1  # Counter
                result.append(item.get("i").get_value())
            print("Users found:", k)  # Print number of results
    return result


def search_order(order_id, driver):  # Search order by id (or show all orders if empty id given)
    # Different approach - download all orders first, filter later
    with driver.session(config.db, SessionType.DATA) as session:  # Access data in the database
        with session.transaction(TransactionType.READ) as transaction:  # Open transaction to read
            typeql_read_query = "match $o isa order, has id $i, has foreign-user-id $fui, " \
                                "has created-date $d, has status $s, has delivery-address $da;" \
                                "get $i, $fui, $d, $s, $da; sort $i asc;"
            # matched results sorted by id in ascending order
            if debug: print("Executing TypeQL read Query: " + typeql_read_query)
            iterator = transaction.query.get(typeql_read_query)  # Execute query
            result = ""
            counter = 0
            for answer in iterator:  # Iterate through result of the query (all orders)
                if order_id == "" or (order_id == answer.get("i").get_value()):  # show all or one with the order_id
                    result += "\nOrder ID:" + str(answer.get("i").get_value())
                    result += " Foreign User-ID:" + str(answer.get("fui").get_value())
                    result += " Date:" + str(answer.get("d").get_value())
                    result += " Status:" + str(answer.get("s").get_value())
                    result += " Delivery address:" + str(answer.get("da").get_value())
                    if result != "":  # If this iteration has something to print
                        print(result)  # Print result
                        counter += 1
                    result = ""  # Reset the variable for next iteration
    return counter


def search_genre(tag_name, driver):  # Search books by genre tag
    if tag_name == "":  # Empty input. But we already showed all tags/genres before
        print("Empty input. Lets look for a Map genre, so you can find what you are looking for.")
        tag_name = "Map"  # Choosing genre instead of an empty input
    TB = TypeDBOptions()  # Initialising a new set of options
    TB.infer = True  # Enabling inference in this new set of options
    with driver.session(config.db, SessionType.DATA) as session:  # Access data in the database
        with session.transaction(TransactionType.READ, TB) as transaction:  # Open transaction to read
            typeql_read_query = "match $g isa genre-tag; $g '" + tag_name + "';" \
                                "$b isa book, has name $n, has ISBN $i, has $g; " \
                                "get $i, $n; sort $i asc;"
            if debug: print("Executing TypeQL read Query: " + typeql_read_query)
            iterator = transaction.query.get(typeql_read_query)  # Execute query
            print("Looking for a", tag_name, "genre. Here is what we have:")
            k = 0  # Counter
            for answer in iterator:  # Iterating through results
                k += 1  # Increase the counter
                result = "\n" + str(k)  # Prepare the positional number of result
                result += " ISBN:" + str(answer.get("i").get_value())  # Prepare ISBN
                result += ", Book title:" + str(answer.get("n").get_value())  # Prepare book name
                print(result)  # Print prepared result
    return k


def show_all_books(driver):  # Just show all books
    print("Showing all books")
    with driver.session(config.db, SessionType.DATA) as session:  # Access data in the database
        with session.transaction(TransactionType.READ) as transaction:  # Open transaction to read
            typeql_read_query = "match $b isa book, has ISBN $i, has name $n, has book-author $ba; " \
                                "get $i, $n, $ba;"
            if debug: print("Executing TypeQL read Query: " + typeql_read_query)
            iterator = transaction.query.get(typeql_read_query)  # Executing match query
            k = 0  # Counter
            for item in iterator:  # Iterating through results
                k += 1
                print(k, item.get("i").get_value(), item.get("n").get_value(), item.get("ba").get_value(), sep=" — ")
                #  Printed result
            print("Total count:", k)  # Printing the counter value after all iterations
    return k


def show_all_users(driver):  # Just show all users
    print("Showing all users")
    with driver.session(config.db, SessionType.DATA) as session:  # Access data in the database
        with session.transaction(TransactionType.READ) as transaction:  # Open transaction to read
            typeql_read_query = "match $u isa user, has id $i, has name $n, has foreign-id $fi; " \
                                "get $i, $n, $fi; sort $fi asc;"  # Limit the number of results by adding " limit 100;"
            # Results sorted by foreign-id in ascending order. Since $fi is a string 9 goes after 88 and before 91
            if debug: print("Executing TypeQL read Query: " + typeql_read_query)
            iterator = transaction.query.get(typeql_read_query)  # Executing query
            k = 0  # Counter
            for item in iterator:  # Iterating through results
                k += 1
                print(k, "- Foreign ID: " + item.get("fi").get_value(), "Name: " + item.get("n").get_value(), "ID: "
                      + item.get("i").get_value())
                # Printed result
            print("Total count:", k)  # Printing counter value after all iterations
    return k


def show_all_genres(driver):  # Just display all genre tags
    with driver.session(config.db, SessionType.DATA) as session:  # Access data in the database
        with session.transaction(TransactionType.READ) as transaction:  # Open transaction to read
            typeql_read_query = "match $g isa genre-tag; get $g;"  # Prepare query
            if debug: print("Executing TypeQL read Query: " + typeql_read_query)
            iterator = transaction.query.get(typeql_read_query)  # Execute transaction
            k = 0  # Counter
            for item in iterator:  # Iterating through all results
                k += 1
                print(k, item.get("g").get_value())  # Printing positional number and genre
            print("Total count:", k)  # Printing counter value after all iterations
    return k


def main():  # This is the main function of this script
    print("Bookstore CRM v.0.0.0.0.1a")
    with TypeDB.core_driver(config.typedb_server_addr) as driver:  # Establishing connection. Once per app
        while True:  # This cycle will repeat until one of the following breaks happen
            x = selection(driver)  # Call selection UI once per cycle
            if x == ResultCode.INPUT_INVALID:  # Unrecognizable answer
                pass  # Return to cycle to call selection() again
            elif x == ResultCode.EXIT:  # Chose to exit
                print("Terminating program.")
                return False  # This stops printing selection of the function UI after exit
            elif x == ResultCode.OK:  # This is no longer viable option. Instead of ResultCode we should send the result
                raise Exception("Unexpected return from the selection function! Check selection() result.")
            else:  # Successfully selected one of the functions — we no longer need to repeat the selection
                return x  # This stops printing selection of the function UI after successful pick


if __name__ == '__main__':
    main()
