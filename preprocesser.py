import re
import pandas as pd
from datetime import datetime
import calendar
import emoji

def llm_dataframe(data):
    # Normalize unicode spaces to regular spaces
    data = data.replace('\u202f', ' ').replace('\xa0', ' ').replace('\u200b', '').strip()

    # Regex to match date/time with optional am/pm + message
    pattern = r'(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}(?: [APMapm]{2})?) - (.+)'

    # Extracting all entries
    entries = re.findall(pattern, data, flags=re.MULTILINE)

    timestamps = []
    messages = []

    for ts, msg in entries:
        ts = ts.strip()
        # Try 24h format
        try:
            dt = datetime.strptime(ts, '%d/%m/%Y, %H:%M')
        except ValueError:
            try:
                dt = datetime.strptime(ts, '%d/%m/%Y, %I:%M %p')
            except ValueError:
                continue
        timestamps.append(dt)
        messages.append(msg)

    df = pd.DataFrame({'datetime': timestamps, 'raw_message': messages})

    # Converting messege_date type
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y, %H:%M - ')
    df.rename(columns={'datetime': 'date'}, inplace=True)

    # Seperating Users & Messeges
    users = []
    messeges = []

    for messege in df['raw_message']:
        entry = re.split('([\w\W]+?):\s', messege)
        if entry[1:]:
            users.append(entry[1])
            messeges.append(entry[2])
        else:
            users.append('group_notification')
            messeges.append(entry[0])

    df['user'] = users
    df['messege'] = messeges
    df.drop(columns=['raw_message'], inplace=True)
    df.rename(columns={'date': 'timestamp'}, inplace=True)
    df['date'] = df['timestamp'].dt.date
    df['time'] = df['timestamp'].dt.time
    df['message_length'] = df['messege'].apply(len)

    def count_emojis(text):
        return sum(1 for char in text if emoji.is_emoji(char))

    df['emoji_count'] = df['messege'].apply(count_emojis)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    copy_df = df
    copy_df = copy_df.sort_values('timestamp')
    response_time = copy_df['timestamp'].diff()
    df['response_time'] = response_time
    df['response_time_str'] = df['response_time'].apply(
        lambda x: str(x).split('.')[0] if pd.notnull(x) else '00:00:00'
    )

    return df


def preprocess(data):
    # Normalize unicode spaces to regular spaces
    data = data.replace('\u202f', ' ').replace('\xa0', ' ').replace('\u200b', '').strip()

    # Regex to match date/time with optional am/pm + message
    pattern = r'(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}(?: [APMapm]{2})?) - (.+)'

    entries = re.findall(pattern, data, flags=re.MULTILINE)

    timestamps = []
    messages = []

    for ts, msg in entries:
        ts = ts.strip()
        # Try 24h format
        try:
            dt = datetime.strptime(ts, '%d/%m/%Y, %H:%M')
        except ValueError:
            try:
                dt = datetime.strptime(ts, '%d/%m/%Y, %I:%M %p')
            except ValueError:
                continue
        timestamps.append(dt)
        messages.append(msg)

    df = pd.DataFrame({'datetime': timestamps, 'raw_message': messages})
    df['datetime'] = pd.to_datetime(df['datetime'])

    users = []
    actual_messages = []

    for msg in df['raw_message']:
        if re.match(r'[^:]+:\s', msg):
            user, message = re.split(r':\s', msg, maxsplit=1)
            users.append(user.strip())
            actual_messages.append(message.strip())
        else:
            users.append('system')
            actual_messages.append(msg.strip())

    df['user'] = users
    df['messege'] = actual_messages
    df.drop(columns=['raw_message'], inplace=True)

    df['date'] = df['datetime']
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['month_name'] = df['date'].dt.month.apply(lambda x: calendar.month_name[x])
    df['only_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()

    # Add period columns
    period = []
    for hour in df['hour']:
        start = hour
        end = 0 if hour == 23 else hour + 1
        period.append(f"{start}-{end}")

    def format_period(hour_str):
        start, end = map(int, hour_str.split('-'))
        def format_hour(h):
            suffix = 'am' if h < 12 else 'pm'
            hour = h % 12 or 12
            return f"{hour}:00{suffix}"
        return f"{format_hour(start)} - {format_hour(end)}"

    df['period'] = [format_period(p) for p in period]



    return df


