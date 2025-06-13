from http.client import responses

from urlextract import URLExtract
from wordcloud import wordcloud, WordCloud
import pandas as pd
from collections import Counter
import emoji
import calendar


def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Number of Messeges
    num_messeges = df.shape[0]

    # Number of Words
    words = []
    for messege in df['messege']:
        words.extend(messege.split())

    # Number of Media
    media = 0
    for messege in df['messege']:
        if messege == "<Media omitted>":
            media += 1

    # Number of links
    extractor = URLExtract()
    links = []
    for messege in df['messege']:
        links.extend(extractor.find_urls(messege))


    return num_messeges, len(words), media, len(links)

def fetch_activity_stats(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns = {'index': 'Name', 'user': 'Name', 'count': 'Percentage'}
    )
    return x, df

def create_wordcloud(selected_user, df):
    # Load Stop Words Mask
    f = open('files/stopwords.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove Media Ommitted messeges
    temp = df[df['messege'] != '<Media omitted>']

    # Remove Group Notifications
    temp = temp[temp['user'] != 'group notification']

    def remove_stop_words(messege):
        y = []
        for word in messege.lower().split():
            if word in messege.lower().split():
                if word not in stop_words and word != '<this' and word != 'edited':
                    y.append(word)
        return " ".join(y)

    wc = WordCloud(width = 500,
                   height = 500,
                   min_font_size = 10,
                   background_color = '#0e1117')
    temp['messege'] = temp['messege'].apply(remove_stop_words)
    df_wc = wc.generate(temp['messege'].str.cat(sep = " "))
    return df_wc

def most_common_words(selected_user, df):
    # Load Stop Words Mask
    f = open('files\stopwords.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove Media Ommitted messeges
    temp = df[df['messege'] != '<Media omitted>']

    # Remove Group Notifications
    temp = temp[temp['user'] != 'group notification']

    # Extracting Words List with all filters
    words = []
    for messege in temp['messege']:
        for word in messege.lower().split():
            if word not in stop_words:
                words.append(word)

    # Generating Count for words
    most_common_words_df = pd.DataFrame(Counter(words).most_common(20))
    most_common_words_df = most_common_words_df[
        most_common_words_df[0] != '<this'
    ]
    most_common_words_df = most_common_words_df[
        most_common_words_df[0] != 'edited>'
        ]
    return most_common_words_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for messege in df['messege']:
        emojis.extend([c for c in messege if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month_name']).count()['messege'].reset_index()

    # Create time labels (for display) and datetime values (for sorting)
    timeline['time_label'] = timeline['month_name'] + "-" + timeline['year'].astype(str)
    timeline['time'] = pd.to_datetime(timeline['year'].astype(str) + "-" + timeline['month_num'].astype(str) + "-01")

    return timeline


def date_wise(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['messege'].reset_index()

    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    week_activity = df['day_name'].value_counts().reset_index()

    return week_activity

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    month_activity = df['month_name'].value_counts().reset_index()

    return month_activity

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Check the column name spelling
    if 'messege' in df.columns:
        value_col = 'messege'
    elif 'message' in df.columns:
        value_col = 'message'
    else:
        raise ValueError("Missing 'message' or 'messege' column.")

    period_order = [
        '12:00am - 1:00am', '1:00am - 2:00am', '2:00am - 3:00am', '3:00am - 4:00am',
        '4:00am - 5:00am', '5:00am - 6:00am', '6:00am - 7:00am', '7:00am - 8:00am',
        '8:00am - 9:00am', '9:00am - 10:00am', '10:00am - 11:00am', '11:00am - 12:00pm',
        '12:00pm - 1:00pm', '1:00pm - 2:00pm', '2:00pm - 3:00pm', '3:00pm - 4:00pm',
        '4:00pm - 5:00pm', '5:00pm - 6:00pm', '6:00pm - 7:00pm', '7:00pm - 8:00pm',
        '8:00pm - 9:00pm', '9:00pm - 10:00pm', '10:00pm - 11:00pm', '11:00pm - 12:00am'
    ]

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Create pivot table
    heatmap_df = df.pivot_table(index='day_name', columns='period', values=value_col, aggfunc='count').fillna(0)
    heatmap_df.reset_index(inplace=True)

    heatmap_long = heatmap_df.melt(id_vars='day_name', var_name='period', value_name='message_count')

    # Set ordering
    heatmap_long['day_name'] = pd.Categorical(heatmap_long['day_name'], categories=day_order, ordered=True)
    heatmap_long['period'] = pd.Categorical(heatmap_long['period'], categories=period_order, ordered=True)

    return heatmap_long

def average_response_time(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    def format_timedelta_pretty(td):
        if pd.isnull(td):
            return "0 seconds"

        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

        return ", ".join(parts)

    df = df[df['response_time'].notnull()]
    avg_response_time = df['response_time'].mean()

    return format_timedelta_pretty(avg_response_time)

def average_messege_length(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    average_msg_length = int(df['message_length'].mean())
    return average_msg_length

def emoji_frequency(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    total_messages = len(df)
    emoji_messages = df[df['emoji_count'] > 0].shape[0]

    if total_messages == 0:
        return 0

    frequency = emoji_messages / total_messages
    return round(frequency * 100, 2)

