import streamlit as st
import plotly.graph_objects as go
import datetime

def render_heatmap(activity_data: list[dict]):
    """Render a GitHub-style activity heatmap using plotly."""
    # Ensure we have data
    if not activity_data:
        st.info("No activity data to display yet. Start solving problems!")
        return

    # Basic setup for Plotly heatmap
    # In a real implementation, we would transform activity_data to map dates to counts
    # and organize by week/day
    
    st.markdown('<div class="heatmap-container">', unsafe_allow_html=True)
    
    # Placeholder for plotly heatmap since full data transformation is complex
    # Here we create a mock figure
    
    fig = go.Figure(data=go.Heatmap(
        z=[[1, 0, 3], [0, 5, 2], [1, 2, 0]],
        x=['Week 1', 'Week 2', 'Week 3'],
        y=['Mon', 'Wed', 'Fri'],
        colorscale=[[0, '#1A1A2E'], [1, '#8B5CF6']],
        showscale=False
    ))
    
    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94A3B8'),
        height=200
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
