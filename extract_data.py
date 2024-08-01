import win32evtlog
from bs4 import BeautifulSoup
import json

# Open event file
query_handle = win32evtlog.EvtQuery('event_raw.evtx', win32evtlog.EvtQueryFilePath)
event_data_list = []
while True:
    events = win32evtlog.EvtNext(query_handle, 1)
    if len(events) == 0:
        break

    for event in events:
        xml_content = win32evtlog.EvtRender(event, win32evtlog.EvtRenderEventXml)
        Bs_data = BeautifulSoup(xml_content, "xml")
        # Extract common tags
        b_unique = Bs_data.find_all('EventRecordID')
        Level = Bs_data.find_all('Level')
        EventID = Bs_data.find_all('EventID')
        Task = Bs_data.find_all('Task')
        Keywords = Bs_data.find_all('Keywords')
        time_created_tag = Bs_data.find("TimeCreated")
        Execution_tag = Bs_data.find("Execution")
        Security = Bs_data.find("Security")
        Event_data = Bs_data.find_all('Data')

        # Extract attribute values
        system_time = time_created_tag["SystemTime"]

        attributes = {
            'SecurityUserID': Security.get("UserID"),
        }

        if Execution_tag:
            attributes['ThreadID'] = Execution_tag.get("ThreadID")
            attributes['ProcessID'] = Execution_tag.get("ProcessID")
        else :
            attributes['ThreadID'] = None
            attributes['ProcessID'] = None


        data_values = []
        for data in Event_data:
            data_name = data.get("Name")
            data_value = data.text
            data_values.append(f"{data_name}: {data_value}")

        # Create a dictionary to store all extracted information
        event_dict = {
            'EventID': EventID[0].text,
            'Level': Level[0].text,
            'EventRecordID': b_unique[0].text,
            'Task': Task[0].text,
            'Keywords': Keywords[0].text,
            'TimeCreated': system_time,
            'ProcessID': attributes['ProcessID'],
            'ThreadID': attributes['ThreadID'],
            'SecurityUserID': attributes['SecurityUserID'],
            'DataValues': ', '.join(data_values)  # Combine data name and value
        }

        event_data_list.append(event_dict)

# Save the list to a JSON file
with open('event_data.json', 'w') as json_file:
    json.dump(event_data_list, json_file)