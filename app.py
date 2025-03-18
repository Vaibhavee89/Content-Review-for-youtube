import streamlit as st
import requests
import pandas as pd
import plotly.express as px

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
                
                if 'items' in stats_response:
                    stats = stats_response['items'][0]['statistics']
                    video_data.append({
                        "Title": title,
                        "Views": int(stats.get("viewCount", 0)),
                        "Likes": int(stats.get("likeCount", 0)),
                        "Comments": int(stats.get("commentCount", 0))
                    })
    
    return pd.DataFrame(video_data)

# Streamlit UI
st.title("YouTube Analytics Dashboard")
api_key = st.text_input("Enter YouTube API Key", type="password")
channel_id = st.text_input("Enter Channel ID")

if st.button("Fetch Data"):
    if api_key and channel_id:
        df = get_video_metrics(api_key, channel_id)
        if not df.empty:
            st.write("### Video Performance Metrics")
            st.dataframe(df)
            
            # Visualizations
            st.write("### Views per Video")
            fig_views = px.bar(df, x="Title", y="Views", title="Views per Video", text_auto=True)
            st.plotly_chart(fig_views)
            
            st.write("### Likes per Video")
            fig_likes = px.bar(df, x="Title", y="Likes", title="Likes per Video", text_auto=True)
            st.plotly_chart(fig_likes)
            
            st.write("### Comments per Video")
            fig_comments = px.bar(df, x="Title", y="Comments", title="Comments per Video", text_auto=True)
            st.plotly_chart(fig_comments)
        else:
            st.warning("No data found. Check API Key and Channel ID.")
    else:
        st.error("Please enter API Key and Channel ID")
