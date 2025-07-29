from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet 
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
from datetime import datetime
import asyncio 

# Dummy data for integration simulation
# Dummy calendar integration data
DUMMY_CALENDAR_MEETINGS = {
    "kim": {
        "nine": {"confirmed": True, "room": "Kiji room", "visitor": "john wick"},
        "eleven": {"confirmed": True, "room": "Kiji room", "visitor": "john wick"},
        "two": {"confirmed": True, "room": "Kiji room", "visitor": "john wick"}
    },
}

# Dummy employee locations data (True means in office, False means not in office)
DUMMY_EMPLOYEE_LOCATIONS = {
    "kim": {
        "nine": True,
        "eleven": False,
        "two": True
    },
}

# Dummy employee replies for Webex messages simulation
DUMMY_EMPLOYEE_REPLY = {
    "kim": {
        "nine": "coming", 
        "eleven": "reschedule", 
        "two": "wait"
    }
}

class ValidateMeetingDetailsForm(FormValidationAction):
    """
    Step 1: Validates the collected slots for the meeting_details_form.
    Ensures that 'visitor_name', 'employee_name', and 'meeting_time' are captured.
    """

    def name(self) -> Text:
        return "validate_meeting_details_form"

    async def validate_visitor_name( 
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        """Validate visitor_name slot."""
        if slot_value:
            return [SlotSet("visitor_name", slot_value)]
        else:
            await asyncio.sleep(2) 
            dispatcher.utter_message(response="utter_ask_visitor_name")
            return [SlotSet("visitor_name", None)]

    async def validate_employee_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        """Validate employee_name slot."""
        if slot_value:
            return [SlotSet("employee_name", slot_value)]
        else:
            await asyncio.sleep(2)
            dispatcher.utter_message(response="utter_ask_employee_name")
            return [SlotSet("employee_name", None)]

    async def validate_meeting_time( 
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        """
        Validate meeting_time slot.
        Converts various time formats to a consistent "HHMM" (24-hour) format.
        """
        if slot_value:
            return [SlotSet("meeting_time", slot_value)]
        else:
            await asyncio.sleep(2)
            dispatcher.utter_message(response="utter_ask_meeting_time")
            return [SlotSet("meeting_time", None)]


class ActionCheckMeetingDetails(Action):
    """
    Step 2: Check for meeting existence.
    This action checks if the meeting details provided by the visitor match an existing meeting in the dummy calendar.
    """

    def name(self) -> Text:
        return "action_check_meeting_details"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict 
    ) -> List[Dict[Text, Any]]:
        employee_name = tracker.get_slot("employee_name")
        meeting_time = tracker.get_slot("meeting_time")
        visitor_name = tracker.get_slot("visitor_name")

        if employee_name and meeting_time and visitor_name:
            dispatcher.utter_message(response="utter_checking_calendar")

        await asyncio.sleep(3) 

        normalized_employee_name = employee_name.lower() if employee_name else ""
        normalized_meeting_time = meeting_time.lower() if meeting_time else ""
        normalized_visitor_name = visitor_name.lower() if visitor_name else ""

        # Check if meeting exists and matches visitor
        if (normalized_employee_name in DUMMY_CALENDAR_MEETINGS and 
            normalized_meeting_time in DUMMY_CALENDAR_MEETINGS[normalized_employee_name] and 
            DUMMY_CALENDAR_MEETINGS[normalized_employee_name][normalized_meeting_time]["confirmed"] and 
            DUMMY_CALENDAR_MEETINGS[normalized_employee_name][normalized_meeting_time]["visitor"].lower() == normalized_visitor_name):

            room = DUMMY_CALENDAR_MEETINGS[normalized_employee_name][normalized_meeting_time]["room"]
            await asyncio.sleep(2)
            dispatcher.utter_message(response="utter_meeting_confirmed",
                                     employee_name=employee_name,
                                     meeting_time=meeting_time,
                                     room_name=room)
            return [
                SlotSet("meeting_confirmed", True),
                SlotSet("room_name", room)
            ]
        else:
            await asyncio.sleep(2)
            dispatcher.utter_message(response="utter_meeting_not_found",
                                     employee_name=employee_name,
                                     meeting_time=meeting_time)
            dispatcher.utter_message(response="utter_ask_recheck_details")
            return [SlotSet("meeting_confirmed", False)]


class ActionLocateEmployee(Action):
    """
    Step 3: Check if employee is in office.
    Check if the employee is in the office at the specified meeting time and respond accordingly.
    """

    def name(self) -> Text:
        return "action_locate_employee"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        employee_name = tracker.get_slot("employee_name")
        meeting_time = tracker.get_slot("meeting_time")
        meeting_confirmed = tracker.get_slot("meeting_confirmed")

        if not meeting_confirmed:
            return []

        normalized_employee_name = employee_name.lower() if employee_name else ""
        normalized_meeting_time = meeting_time.lower() if meeting_time else "" 

        await asyncio.sleep(2)
        dispatcher.utter_message(response="utter_checking_employee_location")

        await asyncio.sleep(3)

        employee_in_office = DUMMY_EMPLOYEE_LOCATIONS.get(normalized_employee_name, {}).get(normalized_meeting_time, False)

        if employee_in_office:
            await asyncio.sleep(2)
            dispatcher.utter_message(response="utter_employee_in_office", employee_name=employee_name)
            return [SlotSet("employee_present", True)]
        else:
            await asyncio.sleep(2)
            dispatcher.utter_message(response="utter_employee_not_in_office_detailed", employee_name=employee_name)
            return [SlotSet("employee_present", False)]


class ActionSendWebexMessage(Action):
    """
    Step 4: Send Webex message to employee and get response.
    This handles both in-office and not-in-office scenarios.
    As both scenarios require sending a message for meeting confirmation.
    """

    def name(self) -> Text:
        return "action_send_webex_message"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        employee_name = tracker.get_slot("employee_name")
        visitor_name = tracker.get_slot("visitor_name")
        meeting_time = tracker.get_slot("meeting_time")
        employee_present = tracker.get_slot("employee_present")

        normalized_employee_name = employee_name.lower() if employee_name else ""
        normalized_meeting_time = meeting_time.lower() if meeting_time else ""

        await asyncio.sleep(2)
        if employee_present:
            dispatcher.utter_message(response="utter_sending_message_in_office", 
                                     employee_name=employee_name, visitor_name=visitor_name)
        else:
            dispatcher.utter_message(response="utter_sending_message_not_in_office", 
                                     employee_name=employee_name, visitor_name=visitor_name)

        await asyncio.sleep(4)
        dispatcher.utter_message(response="utter_waiting_employee_response")

        await asyncio.sleep(3)

        employee_reply = DUMMY_EMPLOYEE_REPLY.get(normalized_employee_name, {}).get(normalized_meeting_time, "coming")

        return [SlotSet("employee_reply", employee_reply)]


class ActionProcessEmployeeResponse(Action):
    """
    Step 5: Process employee's response and inform visitor accordingly.
    """

    def name(self) -> Text:
        return "action_process_employee_response"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        employee_name = tracker.get_slot("employee_name")
        visitor_name = tracker.get_slot("visitor_name")
        employee_reply = tracker.get_slot("employee_reply")

        await asyncio.sleep(2)

        if employee_reply == "coming":
            dispatcher.utter_message(response="utter_employee_coming", 
                                     employee_name=employee_name, visitor_name=visitor_name)
        elif employee_reply == "wait":
            dispatcher.utter_message(response="utter_employee_busy_wait", 
                                     employee_name=employee_name, visitor_name=visitor_name)
        elif employee_reply == "reschedule":
            dispatcher.utter_message(response="utter_employee_reschedule", 
                                     employee_name=employee_name, visitor_name=visitor_name)
        else:
            dispatcher.utter_message(response="utter_employee_busy_wait", 
                                     employee_name=employee_name, visitor_name=visitor_name)

        return []


class ActionFinalInstructions(Action):
    """
    Step 6: Provide final instructions to visitor.
    """

    def name(self) -> Text:
        return "action_final_instructions"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        employee_reply = tracker.get_slot("employee_reply")
        
        await asyncio.sleep(2)
        
        if employee_reply == "reschedule":
            dispatcher.utter_message(response="utter_final_instructions_reschedule")
        else:
            dispatcher.utter_message(response="utter_final_instructions_wait")
        
        return []

class ActionHandOff(Action):
    """
    Custom action to simulate handing off the conversation to a live human agent.
    """

    def name(self) -> Text:
        return "action_hand_off"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        await asyncio.sleep(1)
        dispatcher.utter_message(response="utter_hand_off_to_human")
        return []