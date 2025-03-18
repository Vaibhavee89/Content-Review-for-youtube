import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from textblob import TextBlob

# Function to fetch YouTube Analytics data
def get_video_metrics(api_key, channel_id):
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=10"
    response = requests.get(url)
    data = response.json()
    
    video_data = []
    if 'items' in data:
        for item in data['items']:
            if item['id'].get('videoId'):
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}"
                stats_response = requests.get(stats_url).json()
                
                comments_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={api_key}&maxResults=20"
                comments_response = requests.get(comments_url).json()
                
                positive, negative = 0, 0
                if 'items' in comments_response:
                    for comment in comments_response['items']:
                        text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                        sentiment = TextBlob(text).sentiment.polarity
                        if sentiment > 0:
                            positive += 1
                        elif sentiment < 0:
                            negative += 1
                
                if 'items' in stats_response:
                    stats = stats_response['items'][0]['statistics']
                    video_data.append({
                        "Title": title,
                        "Views": int(stats.get("viewCount", 0)),
                        "Likes": int(stats.get("likeCount", 0)),
                        "Comments": int(stats.get("commentCount", 0)),
                        "Positive Reviews": positive,
                        "Negative Reviews": negative
                    })
    
    return pd.DataFrame(video_data)

# Streamlit UI
st.set_page_config(page_title="YouTube Analytics Dashboard", layout="wide")
st.title("📊 YouTube Analytics Dashboard")
st.markdown("## Analyze your channel's performance with interactive visualizations")

api_key = st.text_input("🔑 Enter YouTube API Key", type="password")
channel_id = st.text_input("🎥 Enter Channel ID")

if st.button("📈 Fetch Data"):
    if api_key and channel_id:
        df = get_video_metrics(api_key, channel_id)
        if not df.empty:
            st.success("Data fetched successfully!")
            
            st.write("### 🎯 Video Performance Metrics")
            st.dataframe(df.style.set_properties(**{'background-color': '#f0f2f6', 'color': 'black'}))
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("### 📊 Views per Video")
                fig_views = px.bar(df, x="Title", y="Views", title="Views per Video", text_auto=True, color="Views", color_continuous_scale="blues")
                st.plotly_chart(fig_views, use_container_width=True)
            
            with col2:
                st.write("### ❤️ Likes per Video")
                fig_likes = px.bar(df, x="Title", y="Likes", title="Likes per Video", text_auto=True, color="Likes", color_continuous_scale="reds")
                st.plotly_chart(fig_likes, use_container_width=True)
            
            st.write("### 💬 Comments per Video")
            fig_comments = px.scatter(df, x="Title", y="Comments", size="Comments", title="Comments per Video", color="Comments", color_continuous_scale="viridis")
            st.plotly_chart(fig_comments, use_container_width=True)
            
            st.write("### 😊 Sentiment Analysis")
            fig_sentiment = px.bar(df, x="Title", y=["Positive Reviews", "Negative Reviews"], title="User Reactions: Positive vs Negative", barmode="group", color_discrete_map={"Positive Reviews": "green", "Negative Reviews": "red"})
            st.plotly_chart(fig_sentiment, use_container_width=True)
            
            st.write("### 🔥 Most Popular Content Over Time")
            fig_popularity = px.line(df.sort_values(by="Views", ascending=False), x="Title", y="Views", title="Popularity of Videos Over Time", markers=True, line_shape='spline', color_discrete_sequence=["orange"])
            st.plotly_chart(fig_popularity, use_container_width=True)
        else:
            st.warning("⚠️ No data found. Check API Key and Channel ID.")
    else:
        st.error("🚨 Please enter API Key and Channel ID")


