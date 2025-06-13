import streamlit as st
import preprocesser, helper, rag
import matplotlib.pyplot as plt
import pandas as pd
import altair as alt
import time

st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="📊",
    layout="wide"
)

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

plt.style.use('dark_background')
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cascadia+Mono&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cascadia Mono', monospace !important;
    }

    /* Override Streamlit titles */
    h1, h2, h3, h4, h5, h6, .stTitle, .stMarkdown {
        font-family: 'Cascadia Mono', monospace !important;
    }

    /* Override dataframe and other widget fonts */
    .stDataFrame, .stTable, .stText, .stSelectbox, .stButton {
        font-family: 'Cascadia Mono', monospace !important;
    }
    </style>
""", unsafe_allow_html=True)



# Creating Sidebar
st.sidebar.title("Whatsapp Chat Analyzer")

# Adding Upload File option in sidebar
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None and 'data' not in st.session_state:
    st.session_state.data = uploaded_file.getvalue().decode("utf-8")
    st.session_state.df = preprocesser.preprocess(st.session_state.data)
    st.session_state.fresh_df = preprocesser.llm_dataframe(st.session_state.data)
    st.session_state.analysis_triggered = False

if 'df' in st.session_state:
    user_list = st.session_state.df['user'].unique().tolist()
    for sys_user in ['group_notification', 'system']:
        if sys_user in user_list:
            user_list.remove(sys_user)
    user_list.sort()
    user_list.insert(0, "Overall")


    # st.dataframe(df) -------------------- # FOR DEBUGGING

    # Fetching Unique Users
    user_list = st.session_state.df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    if 'system' in user_list:
        user_list.remove('system')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis for", user_list)

    if st.sidebar.button("Show Analysis"):
        st.session_state.analysis_triggered = True
        st.session_state.selected_user = selected_user  # Save it across reruns

    if st.sidebar.button("Reset Analysis"):
        for key in ["data", "df", "fresh_df", "analysis_triggered", "selected_user", "rag_chain"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

if st.session_state.get("analysis_triggered", False):
    selected_user = st.session_state.get("selected_user", "Overall")

    # STATS AREA
    num_messeges, words, media, links = helper.fetch_stats(selected_user,st.session_state.df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<h2 style='color: #128C7E; font-family: Cascadia Mono, monospace;'><b>Total Messages</b></h2>", unsafe_allow_html=True)
        st.title(num_messeges)
    with col2:
        st.markdown("<h2 style='color: #128C7E; font-family: Cascadia Mono, monospace;'><b>Total Words</b></h2>", unsafe_allow_html=True)
        st.title(words)
    with col3:
        st.markdown("<h2 style='color: #128C7E; font-family: Cascadia Mono, monospace;'><b>Media Shared</b></h2>",
                    unsafe_allow_html=True)
        st.title(media)
    with col4:
        st.markdown("<h2 style='color: #128C7E; font-family: Cascadia Mono, monospace;'><b>Links Shared</b></h2>",
                    unsafe_allow_html=True)
        st.title(links)

    # MONTHLY TIMELINE
    st.markdown("<h2 style='color: #128C7E; font-family: Cascadia Mono, monospace;'><b>Timeline</b></h2>",
                unsafe_allow_html=True)

    timeline = helper.monthly_timeline(selected_user, st.session_state.df)
    timeline = timeline.rename(columns={'messege': 'message_count'})

    st.markdown(
        "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Monthly Messege Timeline</b></h4>",
        unsafe_allow_html=True)
    timeline_chart = alt.Chart(timeline).mark_line(point=True).encode(
        x=alt.X('time:T', title='Month-Year'),  # Proper time field for sorting
        y=alt.Y('message_count:Q', title='Total Messages'),
        tooltip=['time_label:N', 'message_count:Q']
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(timeline_chart, use_container_width=True)

    # DAILY TIMELINE
    daily_timeline = helper.date_wise(selected_user, st.session_state.df)
    daily_timeline = daily_timeline.rename(columns={'messege': 'message_count'})

    st.markdown(
        "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Daily Messege Timeline</b></h4>",
        unsafe_allow_html=True)
    daily_timeline_chart = alt.Chart(daily_timeline).mark_line(point=True).encode(
        x=alt.X('only_date:T', title='Date'),
        y=alt.Y('message_count:Q', title='Total Messages'),
        tooltip=[alt.Tooltip('only_date:T', title='Date'), 'message_count:Q']
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(daily_timeline_chart, use_container_width=True)

    # FINDING BUSIEST USERS IN THE GROUP
    if selected_user == 'Overall':
        st.markdown(
            "<h2 style='color: #128C7E; font-family: Cascadia Mono, monospace;'><b>Activity Statistics</b></h2>",
            unsafe_allow_html=True)
        x, activity_df = helper.fetch_activity_stats(st.session_state.df)
        fig, ax = plt.subplots()

        activity_chart_df = pd.DataFrame({
            'User': x.index,
            'Message Count': x.values
        })
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Most Active Users</b></h4>",
                unsafe_allow_html=True)
            # Altair Chart
            chart = alt.Chart(activity_chart_df).mark_bar().encode(
                x=alt.X('User:N', sort='-y'),
                y=alt.Y('Message Count:Q'),
                color=alt.Color(value='#25D366'),
                tooltip=['User', 'Message Count']
            ).properties(
                width=300,
                height=400,
            ).configure_axis(
                labelFont='Cascadia Mono',
                titleFont='Cascadia Mono'
            )

            st.altair_chart(chart, use_container_width=True)

        with col2:
            st.markdown(
                "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Activity Percentage</b></h4>",
                unsafe_allow_html=True)
            st.dataframe(activity_df)

        colX, colY = st.columns(2)

        with colX:
            st.markdown(
                "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Week Activity Map</b></h4>",
                unsafe_allow_html=True)
            busy_day = helper.week_activity_map(selected_user, st.session_state.df)
            busy_day.columns = ['day', 'message_count']
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            busy_day['day'] = pd.Categorical(busy_day['day'], categories=day_order, ordered=True)
            busy_day = busy_day.sort_values('day')

            busy_day_chart = alt.Chart(busy_day).mark_bar().encode(
                x=alt.X('day:N', sort=day_order, title='Day of Week'),
                y=alt.Y('message_count:Q', title='Messages'),
                color=alt.Color(value='#25D366'),
                tooltip=['day:N', 'message_count:Q']
            ).properties(
                width=500,
                height=400
            )
            st.altair_chart(busy_day_chart, use_container_width=True)

        with colY:
            st.markdown(
                "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Month Activity Map</b></h4>",
                unsafe_allow_html=True)
            busy_month = helper.month_activity_map(selected_user, st.session_state.df)
            busy_month.columns = ['month', 'message_count']
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                           'October', 'November', 'December']
            busy_month['month'] = pd.Categorical(busy_month['month'], categories=month_order, ordered=True)
            busy_month = busy_month.sort_values('month')

            busy_month_chart = alt.Chart(busy_month).mark_bar().encode(
                x=alt.X('month:N', sort=month_order, title='Month'),
                y=alt.Y('message_count:Q', title='Messages'),
                color=alt.Color(value='#25D366'),
                tooltip=['month:N', 'message_count:Q']
            ).properties(
                width=500,
                height=400
            )
            st.altair_chart(busy_month_chart, use_container_width=True)

    # ACTIVITY HEAT MAP
    st.markdown(
        "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Heat Map</b></h4>",
        unsafe_allow_html=True)

    heatmap_long = helper.activity_heatmap(selected_user, st.session_state.df)
    period_order = [
        '12:00am - 1:00am', '1:00am - 2:00am', '2:00am - 3:00am', '3:00am - 4:00am',
        '4:00am - 5:00am', '5:00am - 6:00am', '6:00am - 7:00am', '7:00am - 8:00am',
        '8:00am - 9:00am', '9:00am - 10:00am', '10:00am - 11:00am', '11:00am - 12:00pm',
        '12:00pm - 1:00pm', '1:00pm - 2:00pm', '2:00pm - 3:00pm', '3:00pm - 4:00pm',
        '4:00pm - 5:00pm', '5:00pm - 6:00pm', '6:00pm - 7:00pm', '7:00pm - 8:00pm',
        '8:00pm - 9:00pm', '9:00pm - 10:00pm', '10:00pm - 11:00pm', '11:00pm - 12:00am'
    ]
    heatmap_chart = alt.Chart(heatmap_long).mark_rect().encode(
        x=alt.X('period:N', title='Time Period', sort=period_order),
        y=alt.Y('day_name:N', title='Day of Week', sort=day_order),
        color=alt.Color('message_count:Q', scale=alt.Scale(scheme='greens'), title='Message Count'),
        tooltip=['day_name:N', 'period:N', 'message_count:Q']
    ).properties(
        width=500,
        height=300
    )

    st.altair_chart(heatmap_chart, use_container_width=True)

    # WORD CLOUD AND MOST COMMON WORDS
    st.markdown(
        "<h2 style='color: #128C7E; font-family: Cascadia Mono, monospace;'><b>Word Usage Analysis</b></h2>",
        unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(
            "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Word Cloud</b></h4>",
            unsafe_allow_html=True)
        wordcloud = helper.create_wordcloud(selected_user, st.session_state.df)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud)
        st.pyplot(fig)

    with col4:
        st.markdown(
            "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Most Used Words</b></h4>",
            unsafe_allow_html=True)
        most_common_words_df = helper.most_common_words(selected_user, st.session_state.df)

        # Convert to proper DataFrame with column names
        most_common_words_df = most_common_words_df.rename(columns={0: 'word', 1: 'count'})

        # Sort by count in descending order
        most_common_words_df = most_common_words_df.sort_values('count', ascending=False)

        # Create Altair chart
        chart = alt.Chart(most_common_words_df).mark_bar().encode(
            x=alt.X('count:Q', title='Count'),
            y=alt.Y('word:N', sort='-x', title='Word'),
            color=alt.Color(value='#25D366')
        ).properties(
            width=700,
            height=700
        )

        st.altair_chart(chart, use_container_width=True)

    # EMOJI STATISTICS
    st.markdown("<h2 style='color: #128C7E; font-family: Cascadia Mono, monospace;'><b>Emoji Analysis</b></h2>",
                unsafe_allow_html=True)
    emoji_df = helper.emoji_helper(selected_user, st.session_state.df)
    emoji_df = emoji_df.rename(columns={0: 'Emoji', 1: 'Count'})

    col5, col6 = st.columns(2)

    with col5:
        st.markdown(
            "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Emoji Statistics</b></h4>",
            unsafe_allow_html=True)
        st.dataframe(emoji_df)
    with col6:
        top_emojis = emoji_df.sort_values('Count', ascending=False).head(10)
        chart = alt.Chart(top_emojis).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Emoji", type="nominal"),
            tooltip=["Emoji", "Count"]
        ).properties(
            width=300,
            height=300
        )

        st.markdown(
            "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Visual Overview</b></h4>",
            unsafe_allow_html=True)
        st.altair_chart(chart, use_container_width=True)

    # ------------------FRESH DATA FRAME FOR LLM---------------------------------------------
    fresh_df = preprocesser.llm_dataframe(st.session_state.data)
    st.session_state.fresh_df = fresh_df


    st.dataframe(fresh_df)  # ------------ FOR DEBUGGING

    st.markdown("<h2 style='color: #128C7E; font-family: Cascadia Mono, monospace;'><b>Additional Metrics</b></h2>",
                unsafe_allow_html=True)

    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown(
            "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Average Response Time</b></h4>",
            unsafe_allow_html=True)
        st.title(helper.average_response_time(selected_user, st.session_state.fresh_df))

    with colB:
        st.markdown(
            "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Average Messege Length</b></h4>",
            unsafe_allow_html=True)
        st.title(str(helper.average_messege_length(selected_user, st.session_state.fresh_df)) + " characters")

    with colC:
        st.markdown(
            "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Emoji Frequency</b></h4>",
            unsafe_allow_html=True)
        st.title(str(helper.emoji_frequency(selected_user, st.session_state.fresh_df)) + "%")

    st.markdown("<h2 style='color: #128C7E; font-family: Cascadia Mono, monospace;'><b>ChatGuru</b></h2>",
                unsafe_allow_html=True)
    st.markdown(
        "<h4 style='color: #dcf8c6; font-family: Cascadia Mono, monospace;'><b>Curious about this conversation? Just ask the ChatGuru — he's always ready to help</b></h4>",
        unsafe_allow_html=True)

    with st.spinner("Loading ChatGuru..."):
        # Setting up RAG Chain
        if 'rag_chain' not in st.session_state:
            st.session_state.rag_chain = rag.get_rag_chain(st.session_state.fresh_df)
            time.sleep(1.5)

    # Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Displaying previous messeges
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Quering the RAG
    query = st.chat_input("Ask your chat something...")
    if query:
        st.chat_message("user").markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})

        result = rag.query_rag(st.session_state.rag_chain, query)
        response = result["result"]

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})





