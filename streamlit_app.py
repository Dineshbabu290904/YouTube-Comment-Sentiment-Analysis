import streamlit as st
import os
from Senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from YoutubeCommentScrapper import save_video_comments_to_csv, get_channel_info, youtube, get_channel_id, get_video_stats

def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))

# Page configuration
st.set_page_config(page_title="YouTube Sentiment Analysis", page_icon="🎥", layout="wide")

# Sidebar
st.sidebar.title("YouTube Sentiment Analysis")
st.sidebar.header("Enter YouTube Link")
youtube_link = st.sidebar.text_input("Link")
directory_path = os.getcwd()

# Hide default Streamlit elements
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.sidebar.success("Valid YouTube link detected!")
        channel_id = get_channel_id(video_id)
        csv_file = save_video_comments_to_csv(video_id)
        delete_non_matching_csv_files(directory_path, video_id)
        st.sidebar.write("Comments saved to CSV!")
        st.sidebar.download_button(label="Download Comments", data=open(csv_file, 'rb').read(),
                                    file_name=os.path.basename(csv_file), mime="text/csv")

        # Channel Info
        channel_info = get_channel_info(youtube, channel_id)
        st.title(f"📺 {channel_info['channel_title']}'s Dashboard")
        
        with st.expander("📊 Channel Information"):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(channel_info['channel_logo_url'], width=150)
            with col2:
                st.subheader(f"Channel Name: {channel_info['channel_title']}")
                st.write(f"**Subscriber Count:** {channel_info['subscriber_count']}")
                st.write(f"**Total Videos:** {channel_info['video_count']}")
                st.write(f"**Created On:** {channel_info['channel_created_date'][:10]}")
                st.write(f"**Description:** {channel_info['channel_description']}")

        # Video Info
        stats = get_video_stats(video_id)
        with st.expander("🎥 Video Information"):
            col3, col4, col5 = st.columns(3)
            col3.metric("Views", stats["viewCount"])
            col4.metric("Likes", stats["likeCount"])
            col5.metric("Comments", stats["commentCount"])
            st.video(youtube_link)

        # Sentiment Analysis
        results = analyze_sentiment(csv_file)
        with st.expander("💬 Sentiment Analysis"):
            col6, col7, col8 = st.columns(3)
            col6.metric("Positive Comments", results['num_positive'], delta_color="normal")
            col7.metric("Negative Comments", results['num_negative'], delta_color="inverse")
            col8.metric("Neutral Comments", results['num_neutral'], delta_color="off")

            st.subheader("Sentiment Distribution")
            bar_chart(csv_file)
            plot_sentiment(csv_file)

    else:
        st.sidebar.error("Invalid YouTube link. Please enter a valid URL.")
else:
    st.sidebar.info("Enter a YouTube link to begin analysis.")
