"""
Me-API Playground - Streamlit Frontend
Interactive UI for the portfolio API
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from typing import Optional, Dict, List
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin123")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "hello123")

# Page config
st.set_page_config(
    page_title="Me-API Playground",
    page_icon="👨‍💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .profile-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .profile-name {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .profile-bio {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    .skill-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        border-radius: 20px;
        background-color: #667eea;
        color: white;
        font-size: 0.9rem;
    }
    .project-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: box-shadow 0.3s;
    }
    .project-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .work-card {
        border-left: 4px solid #667eea;
        padding-left: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .stat-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ===== API Helper Functions =====
def get_profile() -> Optional[Dict]:
    """Fetch profile data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/profile", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch profile: {str(e)}")
        return None


def get_projects(skill: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
    """Fetch projects with optional filters"""
    try:
        params = {}
        if skill:
            params['skill'] = skill
        if status:
            params['status'] = status
        
        response = requests.get(f"{API_BASE_URL}/projects", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch projects: {str(e)}")
        return []


def get_top_skills(limit: int = 10) -> List[Dict]:
    """Fetch top skills by project count"""
    try:
        response = requests.get(f"{API_BASE_URL}/skills/top", params={"limit": limit}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch top skills: {str(e)}")
        return []


def search_content(query: str) -> List[Dict]:
    """Search across projects and work experience"""
    try:
        response = requests.get(f"{API_BASE_URL}/search", params={"q": query}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Search failed: {str(e)}")
        return []


def check_health() -> Optional[Dict]:
    """Check API health"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


# ===== UI Components =====
def render_profile_card(profile: Dict):
    """Render profile header card"""
    st.markdown(f"""
    <div class="profile-card">
        <div class="profile-name">{profile['name']}</div>
        <div class="profile-bio">{profile.get('bio', '')}</div>
        <div style="margin-top: 1rem;">
            📧 {profile['email']} | 📍 {profile.get('location', 'N/A')} | 📱 {profile.get('phone', 'N/A')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Social links
    if profile.get('social_links'):
        st.markdown("### 🔗 Connect With Me")
        cols = st.columns(len(profile['social_links']))
        for idx, link in enumerate(profile['social_links']):
            with cols[idx]:
                st.markdown(f"[{link['platform']}]({link['url']})")


def render_stats(profile: Dict):
    """Render statistics overview"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(profile.get('projects', []))}</div>
            <div class="stat-label">Projects</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(profile.get('skills', []))}</div>
            <div class="stat-label">Skills</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(profile.get('work_experience', []))}</div>
            <div class="stat-label">Work Experiences</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(profile.get('education', []))}</div>
            <div class="stat-label">Education</div>
        </div>
        """, unsafe_allow_html=True)


def render_projects(projects: List[Dict]):
    """Render projects list"""
    if not projects:
        st.info("No projects found.")
        return
    
    for project in projects:
        with st.container():
            st.markdown(f"""
            <div class="project-card">
                <h3>{project['name']}</h3>
                <p>{project.get('description', 'No description available')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Project details
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                if project.get('skills'):
                    st.markdown("**Technologies:**")
                    skills_html = "".join([
                        f'<span class="skill-badge">{skill["name"]}</span>'
                        for skill in project['skills']
                    ])
                    st.markdown(skills_html, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**Status:** {project.get('status', 'N/A').title()}")
                st.markdown(f"**Duration:** {project.get('start_date', 'N/A')} - {project.get('end_date', 'N/A')}")
            
            with col3:
                if project.get('github_url'):
                    st.markdown(f"[GitHub]({project['github_url']})")
                if project.get('demo_url'):
                    st.markdown(f"[Live Demo]({project['demo_url']})")
            
            st.markdown("---")


def render_work_experience(experiences: List[Dict]):
    """Render work experience timeline"""
    if not experiences:
        st.info("No work experience found.")
        return
    
    for exp in experiences:
        st.markdown(f"""
        <div class="work-card">
            <h3>{exp['position']}</h3>
            <h4>{exp['company']} • {exp.get('location', 'Remote')}</h4>
            <p><em>{exp.get('start_date', 'N/A')} - {exp.get('end_date', 'Present')}</em></p>
            <p>{exp.get('description', '')}</p>
        </div>
        """, unsafe_allow_html=True)


def render_education(education: List[Dict]):
    """Render education history"""
    if not education:
        st.info("No education records found.")
        return
    
    for edu in education:
        st.markdown(f"""
        ### {edu['degree']}
        **{edu['institution']}** • {edu.get('field', '')}
        
        {edu.get('start_date', 'N/A')} - {edu.get('end_date', 'N/A')}
        
        {f"GPA: {edu['gpa']}" if edu.get('gpa') else ''}
        
        {edu.get('description', '')}
        """)
        st.markdown("---")


def render_skills_chart(top_skills: List[Dict]):
    """Render interactive skills chart"""
    if not top_skills:
        st.info("No skills data available.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(top_skills)
    
    # Bar chart for project count
    fig = px.bar(
        df,
        x='name',
        y='project_count',
        color='category',
        title='Top Skills by Project Count',
        labels={'name': 'Skill', 'project_count': 'Projects', 'category': 'Category'},
        height=400
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Experience years chart
    if 'years_experience' in df.columns:
        fig2 = px.scatter(
            df,
            x='years_experience',
            y='project_count',
            size='project_count',
            color='category',
            hover_data=['name', 'level'],
            title='Skills: Experience vs Usage',
            labels={'years_experience': 'Years of Experience', 'project_count': 'Projects'},
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)


# ===== Main App =====
def main():
    # Sidebar
    with st.sidebar:
        st.title("🎯 Navigation")
        
        # Health check
        health = check_health()
        if health:
            status_color = "🟢" if health['database'] == "connected" else "🔴"
            st.markdown(f"{status_color} API Status: {health['status'].title()}")
            st.markdown(f"Database: {health['database'].title()}")
        else:
            st.markdown("🔴 API Offline")
        
        st.markdown("---")
        
        page = st.radio(
            "Select Page",
            ["🏠 Home", "💼 Projects", "🎓 Experience & Education", "🔧 Skills", "🔍 Search"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 🔗 Quick Links")
        st.markdown(f"[API Docs]({API_BASE_URL}/docs)")
        st.markdown(f"[API Root]({API_BASE_URL})")
    
    # Main content
    profile = get_profile()
    
    if not profile:
        st.error("⚠️ Unable to load profile. Please ensure the backend is running.")
        st.code(f"Backend URL: {API_BASE_URL}")
        return
    
    # Home Page
    if page == "🏠 Home":
        st.title("Welcome to My Portfolio")
        render_profile_card(profile)
        
        st.markdown("## 📊 Quick Stats")
        render_stats(profile)
        
        st.markdown("## 🚀 Featured Projects")
        featured_projects = profile.get('projects', [])[:3]  # Show top 3
        render_projects(featured_projects)
        
        st.markdown("## 🏆 Top Skills")
        top_skills = get_top_skills(limit=8)
        if top_skills:
            skills_html = "".join([
                f'<span class="skill-badge">{skill["name"]} ({skill["project_count"]})</span>'
                for skill in top_skills
            ])
            st.markdown(skills_html, unsafe_allow_html=True)
    
    # Projects Page
    elif page == "💼 Projects":
        st.title("Projects Portfolio")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            skill_filter = st.selectbox(
                "Filter by Skill",
                ["All"] + [skill['name'] for skill in profile.get('skills', [])],
                index=0
            )
        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "completed", "in-progress", "archived"],
                index=0
            )
        
        # Apply filters
        skill_param = None if skill_filter == "All" else skill_filter
        status_param = None if status_filter == "All" else status_filter
        
        projects = get_projects(skill=skill_param, status=status_param)
        st.markdown(f"### Found {len(projects)} project(s)")
        render_projects(projects)
    
    # Experience & Education Page
    elif page == "🎓 Experience & Education":
        st.title("Professional Experience & Education")
        
        tab1, tab2 = st.tabs(["💼 Work Experience", "🎓 Education"])
        
        with tab1:
            render_work_experience(profile.get('work_experience', []))
        
        with tab2:
            render_education(profile.get('education', []))
    
    # Skills Page
    elif page == "🔧 Skills":
        st.title("Skills & Expertise")
        
        # Get top skills with visualization
        limit = st.slider("Number of skills to display", 5, 20, 10)
        top_skills = get_top_skills(limit=limit)
        
        render_skills_chart(top_skills)
        
        # Skills breakdown by category
        st.markdown("## 📋 Skills by Category")
        skills_by_category = {}
        for skill in profile.get('skills', []):
            category = skill.get('category', 'Other')
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill)
        
        for category, skills in skills_by_category.items():
            with st.expander(f"{category.title()} ({len(skills)})"):
                for skill in skills:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{skill['name']}**")
                    with col2:
                        st.markdown(f"Level: {skill.get('level', 'N/A').title()}")
                    with col3:
                        st.markdown(f"{skill.get('years_experience', 0)} years")
    
    # Search Page
    elif page == "🔍 Search":
        st.title("Search Portfolio")
        
        search_query = st.text_input(
            "Search projects and work experience",
            placeholder="e.g., React, API, microservices..."
        )
        
        if search_query:
            with st.spinner("Searching..."):
                results = search_content(search_query)
            
            if results:
                st.success(f"Found {len(results)} result(s)")
                
                for result in results:
                    st.markdown(f"""
                    ### {result['title']}
                    **Type:** {result['type'].replace('_', ' ').title()}  
                    **Relevance:** {'⭐' * int(result.get('relevance_score', 1))}
                    
                    {result.get('description', 'No description')}
                    """)
                    st.markdown("---")
            else:
                st.info("No results found. Try a different search term.")


if __name__ == "__main__":
    main()