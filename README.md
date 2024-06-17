# ScheduleBot: A Smart Event and Reminder Manager

ScheduleBot is a chatbot designed to manage events and reminders on the Matrix platform. It understands natural language inputs and performs tasks such as scheduling, canceling, and updating events. The bot leverages regex-based parsing for flexible language input and JSON for data storage.

## Features

### 1. **Auto-Join Skill**
   - Automatically accepts messages from new users.
   - Sends a welcome message with usage instructions.

### 2. **Scheduling Events**
   - Detects sentences with "remember" to schedule tasks.
   - Extracts task name, date, time, and recurrence from user input.
   - Supports both numeric and textual date formats.
   - Saves tasks with default settings if recurrence or flags aren't specified.
   - Uses `extract_schedule_info` function for flexible multi-sentence input.

### 3. **Canceling Tasks**
   - Identifies "cancel" commands in user input.
   - Matches tasks with user-provided details in the database.
   - Updates the task's `canceled` flag and notifies the user.

### 4. **Updating Tasks**
   - Recognizes "change" commands to update existing tasks.
   - Extracts old and new dates and updates the corresponding task.
   - Provides user feedback on successful or failed updates.

### 5. **Marking Tasks as Done**
   - Detects "done" or "finished" keywords in user input.
   - Matches tasks and marks them as completed in the database.
   - Notifies users of successful updates.

### 6. **Retrieving Daily/Weekly Plans**
   - Processes queries like "show" or "tell" to retrieve tasks for specific dates or ranges.
   - Displays matching tasks with their details.

## Data Handling
- Tasks are stored in JSON format for persistence.
- JSON operations include saving, retrieving, and updating tasks dynamically.

## Installation and Usage
1. Ensure you have Python and Matrix SDK installed.
2. Clone the repository and navigate to the project directory.
3. Use the commands in `note.txt` to set up and run the bot.
4. Add the bot to a Matrix room and start interacting with it.

## Bot Identifier
- Name: `@schedulebot:matrix.org`

## Example Commands
- **Schedule Task:**  
  `Remember to submit the report on Monday at 10 AM.`  
- **Cancel Task:**  
  `Cancel the meeting on Tuesday at 3 PM.`  
- **Update Task:**  
  `Change the doctor's appointment to Friday at 2 PM.`  
- **Mark as Done:**  
  `The project presentation is done.`  
- **Retrieve Tasks:**  
  `Show me the tasks for this week.`

## Testing
- Sample test sentences are included as comments within the code for various operations.

## Acknowledgments
This bot demonstrates advanced regex-based natural language processing and efficient task management using JSON. Built for seamless scheduling on the Matrix platform.

