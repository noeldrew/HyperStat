import datetime
import os
import threading
import time
from datetime import datetime, date, timedelta
import sys
from typing import Any

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLabel, QHBoxLayout, QVBoxLayout

from HyperPassAPI import HyperPassAPI


class LineItem(QWidget):

    def __init__(self, label_text: str, value_text: str):
        super(LineItem, self).__init__()
        self.label = QLabel(label_text)
        self.value = QLabel(value_text)
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.value)
        self.setLayout(layout)
class MainWindow(QMainWindow):
    _ticket_types: dict = {
        'adult': 'a76bf0b8-8295-4551-a1fd-ca3ce7fcdfd0',
        'child': 'c230e20d-2e0a-4e05-bc86-0c30ad022fc0'
    }

    LOOK_BACK_PERIOD: int = 48
    _counter: int = 1

    def __init__(self):
        super().__init__()
        self._api = None
        self._tickets_to_date = None

        self.setWindowTitle("My App")
        self.setFixedSize(400, 200)
        self.stage = QWidget()
        self.setCentralWidget(self.stage)

        self.total_tickets_sold_label = LineItem('Total tickets sold', str(0))
        self.total_adults_sold_label = LineItem('Total adults sold', str(0))
        self.total_child_sold_label = LineItem('Total child sold', str(0))

        layout = QVBoxLayout()
        layout.addWidget(self.total_tickets_sold_label)
        layout.addWidget(self.total_adults_sold_label)
        layout.addWidget(self.total_child_sold_label)
        self.stage.setLayout(layout)

        self._getAPIAuthorisationToken(self._handleAPIAuthorise)

    def _handleButtonClick(self) -> None:
        print('still picking up button clicks')

    def _getAPIAuthorisationToken(self, callback: Any) -> None:
        self._api: HyperPassAPI = HyperPassAPI()
        if self._api.getClientAuthorisationToken():
            callback()

    def _handleAPIAuthorise(self) -> None:
        self._setup_update_timer()
        self.updateData()

    def _setup_update_timer(self) -> None:
        self._timer = threading.Timer(60.0, self.updateData)
        self._timer.daemon = True

    def updateData(self) -> None:
        ticket_types = self._api.getTicketTypes()
        api_response = self._api.getAllTicketsToDate()
        # api_response = self._api.getAllTicketsForPastPeriod(self.LOOK_BACK_PERIOD)
        tickets = api_response['tickets']
        self._processTickets(tickets)

        total_tickets = self._getTotal(tickets)
        print(f'{total_tickets} tickets sold so far since zero hour (07-12-2022  20:00 GST')
        self.total_tickets_sold_label.value.setText(str(total_tickets))
        # self.total_tickets_sold_label.value.setText(str(self._counter))

        for t in ticket_types:
            count = self._getTotalByType(tickets, t['id'])
            if t['name'] == 'Entry Ticket':
                self.total_adults_sold_label.value.setText(str(count))
            else:
                self.total_child_sold_label.value.setText(str(count))
            print(f'    {count} x {t["name"]}')

        hours = self._getTotalsPerHourPerPeriod(tickets, self.LOOK_BACK_PERIOD)
        print(f'hourly totals for the last {self.LOOK_BACK_PERIOD} hours')

        for count, hour in enumerate(hours):
            print(f'{count}    {hour["start_time"]}        {len(hour["tickets"])}')

        self._counter += 1

        self._setup_update_timer()
        self._timer.start()

    def _processTickets(self, tickets: list) -> None:
        print('processing tickets list')
        for ticket in tickets:
            print(f'    {ticket}')

    def _getTotal(self, ticket_list: list) -> int:
        return len(ticket_list)

    def _getTotalByType(self, ticket_list: list, ticket_type: str) -> int:
        count: int = sum(1 for t in ticket_list if t['ticket_type'] == ticket_type)
        return count

    def _getTotalsPerHourPerPeriod(self, ticket_list: list, look_back: int) -> list:
        hourly_totals: list = []
        utc_offset = timedelta(hours=4)
        look_back_offset = timedelta(hours=look_back)
        delta = timedelta(minutes=60)
        lookback_end_time = datetime.now() - utc_offset - look_back_offset

        bracket_end_time = datetime.now() - utc_offset
        bracket_start_time = bracket_end_time - delta

        while bracket_start_time >= lookback_end_time:
            grouping = self._getTotalsPerHour(bracket_start_time, bracket_end_time, ticket_list)
            hourly_totals.append(grouping)
            bracket_end_time = bracket_start_time
            bracket_start_time -= delta

        return hourly_totals

    def _getTotalsPerHour(self, start_time, end_time, ticket_list) -> dict:
        tickets: list = []
        for t in ticket_list:
            timestamp = datetime.fromisoformat(t['created_at'].replace('Z', ''))
            if timestamp > start_time and timestamp < end_time:
                tickets.append(t)
        return {
            'start_time': start_time,
            'end_time'  : end_time,
            'tickets'   : tickets
        }




app = QApplication(sys.argv)

window = MainWindow()
window.show()

# api: HyperPassAPI = HyperPassAPI()
# if api.getClientAuthorisationToken():
#     tickets_to_date = api.getAllTicketsToDate()
#     print(tickets_to_date)


app.exec()


