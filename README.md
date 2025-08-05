# RASA Component for Virtual Receptionist

This codebase are used for processing the input from Webex component and produce the output for Heygen to vocalize. The `action.py` simulates the backend integration of the virtual receptionist capabilities.

## Prerequisites

Ensure you have the following installed:

* **Python 3.8+**: Rasa requires a modern Python version.

* **Rasa Open Source Version**: You can install it via pip:

    ```bash
    pip install rasa-sdk
    ```

* **Virtual Environment (Recommended)**: This is to manage project dependencies.

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    .venv\Scripts\activate     # On Windows
    ```

## Main Project Files
* `domain.yml`: Defines the intents, entities, slots, forms, and responses of the assistant.
* `nlu.yml`: Contains Natural Language Understanding (NLU) training data, mapping user inputs to intents and extracting entities.
* `rules.yml`: Defines short, fixed sequences of turns that the assistant should follow.
* `stories.yml`: Defines longer, example conversations that the assistant should be able to handle.
* `actions.py`: Contains custom actions that the assistant can execute, involving integrations and more complex logic. In this code it is used to simulate integration with Google calendar, employee's location checking and webex messaging simulation.

## Setup RASA

Follow these steps to get the RASA up and running:

1.  **Navigate to the Project Directory**:
    Make sure you are in the root directory of your Rasa project where `config.yml`, `credentials.yml`, `domain.yml`, `endpoints.yml`, and the folders `actions`, `data`, `models` and `tests` are located.

2.  **Train the Rasa Model**:
    This command will train the NLU and Core models based on your `nlu.yml`, `rules.yml`, and `stories.yml` files.

    ```bash
    rasa train
    ```

3.  **Run the Actions Server**:
    Open a **new terminal window** and execute this command:

    ```bash
    rasa run actions
    ```

    Keep this terminal window open while you interact with the Rasa assistant.

4.  **Enable API and Run the Rasa Assistant**:
    In your **first terminal window** (where you run `rasa train`), start the Rasa assistant with the API enabled and CORS configured to allow requests from any origin.

    ```bash
    rasa shell --cors "*"
    ```

## `actions.py` Overview

The `actions.py` file simulates interactions with external systems like calendar applications and employee location checking integrations.

### Dummy Values for Simulation

The `actions.py` uses several dummy dictionaries to simulate external integration responses:

* **`DUMMY_CALENDAR_MEETINGS`**:

    * Simulates response from a calendar system that stores confirmed meetings.

* **`DUMMY_EMPLOYEE_LOCATIONS`**:

    * Simulates response from Cisco Space employee location tracking system.

* **`DUMMY_EMPLOYEE_REPLY`**:

    * Simulates the employee's response to a message sent by the receptionist via Webex Messaging.

### Functions

* **`ValidateMeetingDetailsForm`**:

    * This function ensures the required slots (`visitor_name`, `employee_name`, `meeting_time`) for the `meeting_details_form` are correctly extracted from the user's input.

* **`ActionCheckMeetingDetails`**:

    * Simulates checking a calendar system. It uses `DUMMY_CALENDAR_MEETINGS` to determine if a meeting exists for the provided details. It sets the `meeting_confirmed` and `room_name` slots.

* **`ActionLocateEmployee`**:

    * Simulates querying a location tracking system. It uses `DUMMY_EMPLOYEE_LOCATIONS` to check if the employee is currently in the office at the specified meeting time.

* **`ActionSendWebexMessage`**:

    * Simulates sending a message to the employee (e.g., via Webex) to inform them about their visitor. It then retrieves a dummy reply from `DUMMY_EMPLOYEE_REPLY` and sets the `employee_reply` slot. This action handles both scenarios where the employee is in or out of the office.

* **`ActionProcessEmployeeResponse`**:

    * Interprets the `employee_reply` slot and provides an appropriate response to the visitor, informing them whether the employee is coming, needs them to wait, or needs to reschedule.

* **`ActionFinalInstructions`**:

    * Provides final instructions to the visitor based on the outcome of the meeting check and employee response.

* **`ActionHandOff`**:

    * Simulates transferring the conversation to a live human agent.