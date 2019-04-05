"""
CSC148, Winter 2019
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


# TODO: Implement the MTMContract, TermContract, and PrepaidContract
class TermContract(Contract):
    """ A contract for a phone line

        All users using this contract will have a deposit fee, whenever the user
        cancell the contract early, the deposit will be taken. The contract
        also comes with free minutes, the free minutes are used up first and
        refreshes each month.

        === Public Attributes ===
        start:
             starting date for the contracts
        bill:
             bill for this contract for the last month of call
        end:
             the date of end for the contract
        """

    start: datetime.datetime
    bill: Bill
    end: datetime.datetime
    current_date: datetime.datetime

    def __init__(self, start: datetime.datetime, end: datetime.datetime) -> None:
        self.start = start
        self.current_date = self.start
        self.end = end

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.bill = bill
        self.bill.set_rates('term', 0.1)
        self.bill.add_fixed_cost(20.00)
        self.bill.free_min = 0

        if month == self.start.month and year == self.start.year:
            self.bill.add_fixed_cost(300.00)

        self.current_date = datetime.datetime(year, month, 1)

    def bill_call(self, call: Call) -> None:
        if self.bill.free_min < 100:
            if (self.bill.free_min + ceil(call.duration / 60.0)) <= 100:
                self.bill.add_free_minutes(ceil(call.duration / 60.0))
            else:
                temp = (ceil(call.duration / 60.0) + self.bill.free_min) - 100
                self.bill.add_billed_minutes(temp)
                self.bill.free_min = 100
        else:
            self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        if self.current_date > self.end:
            self.bill.add_fixed_cost(-300.0)  # returning deposit
        Contract.cancel_contract(self)


class MTMContract(Contract):
    """ A contract for a phone line

            All users using this contract does not have any deposit or free mins
            the calling rate is higher than TermContract, but it has no end date

            === Public Attributes ===
            start:
                 starting date for the contracts
            bill:
                 bill for this contract for the last month of call
    """

    start: datetime.date
    bill: Bill

    def __init__(self, start: datetime.date) -> None:
        self.start = start

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.bill = bill
        bill.set_rates('mtm', 0.05)
        bill.add_fixed_cost(50.00)


class PrepaidContract(Contract):
    """ A contract for a phone line

                All users using this contract has a start date, and a balance
                a negative balance means the user has paid this much before hand
                the balance will start off negative, whenever the balance is
                more than -10, it needs to be topped up to -25. If the balance
                is negative when cancelling contract, the balance is forfeited,
                if it's positive, then call Contract.cancel_contract

                === Public Attributes ===
                start:
                     starting date for the contracts
                bill:
                     bill for this contract for the last month of call
                balance:
                     the balance for this contract
    """

    start: datetime.date
    bill: Bill
    balance: float

    def __init__(self, start: datetime.date, balance: float) -> None:
        self.start = start
        self.balance = -balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:

        self.bill = bill
        bill.set_rates('prepaid', 0.025)
        bill.add_fixed_cost(self.balance)

        if self.balance > -10:
            self.balance -= 25
            bill.add_fixed_cost(25)

    def cancel_contract(self) -> float:
        if self.balance <= 0:
            self.start = None
        else:
            Contract.cancel_contract(self)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
