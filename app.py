import streamlit as st
import pandas as pd
import gspread as gs
from google.oauth2 import service_account
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

sheet_url = st.secrets["private_gsheets_url"]
scopes = ['https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes = scopes
)

gc = gs.authorize(credentials)
sh = gc.open_by_url(sheet_url)
ws = sh.worksheet('Data')
df = pd.DataFrame(ws.get_all_records())


#st.write(df.head(10))

# ---- MAINPAGE ----
st.set_page_config(page_title="Consumer Financial Complaints Dashboard",layout="wide",page_icon=":sparkles:")
st.header("Consumer Financial Complaints Dashboard")
st.subheader("Display Data for “All States” or “Colorado” State (Based on Filter Selected)")

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
state = st.sidebar.multiselect(
    "Select the State:",
    options=df["state"].unique(),
    default=df["state"].unique()
)

# df_selection = df.query(
#     "state == @state"
# )


# TOP KPI's
#Total Number of Complaints
no_of_Complaint=df['Count of complaint_id'].count()

#Number of Complaints Status : Closed
Complains_status_closed=df[df['company_response']=='%Closed%']['Count of complaint_id'].count()

#Timely Responded Complaints : Percentage
timely_responded_complaints=df[
    df['timely']=='Yes']['Count of complaint_id'].count()/(df['Count of complaint_id'].count())*100

#Total Number of Complaints Status : In progress
complaints_progress=df[df['company_response']=='In progress']['Count of complaint_id'].sum()

# KPI GRID

with st.container():
    col1, col2, col3,col4,col5 = st.columns([1,1,1,1,1])
    col1.metric("Total #of Complaints",no_of_Complaint)
    col2.metric("Status: Closed",Complains_status_closed)
    col3.metric(" %of Timely Responded",round(timely_responded_complaints, 2))
    col4.metric("Status: Progress",complaints_progress)
    state=col5.selectbox( 'Select the State',options=df['state'].unique())
    
    df_selection=df.query(
        "state == @state"
        )

# Vertical bar-chart

complaints_by_product=df.groupby('product').sum()[['Count of complaint_id']
].sort_values(by='Count of complaint_id')

viz_complaints_by_product=px.bar(complaints_by_product,x=complaints_by_product.index,
y='Count of complaint_id',

 orientation='v',
    color_discrete_sequence=["#200d80"] * len(complaints_by_product),
    template="plotly_dark",
)

viz_complaints_by_product.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# Line-chart

complaints_over_time = df.groupby('Month Year').sum()[['Count of complaint_id']
].sort_values(by='Count of complaint_id')
viz_complaints_over_time=px.line(complaints_over_time,y='Count of complaint_id',
x=complaints_over_time.index,
    color_discrete_sequence=["#942390"] * len(complaints_over_time),
    template="plotly_dark",
)
viz_complaints_over_time.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# Pie-Chart
complaints_by_channel=df.groupby('submitted_via').sum()[['Count of complaint_id']
].sort_values(by='Count of complaint_id')
viz_complaints_by_channel=px.pie(complaints_by_channel,values='Count of complaint_id',
names=complaints_by_channel.index,
    color_discrete_sequence=["#EC6B56","#FFC154","#47B39C","#FFF1C9","#F7B7A3"] * len(complaints_by_channel),
    template="plotly_dark",
)
viz_complaints_by_channel.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)


# Tree-Map 

state=df['state']
issue=df['issue']
sub_issue=df['sub_issue']
count_of_complaints=df['Count of complaint_id']
viz_tree=px.treemap(df,path=['state','issue','sub_issue'],values=count_of_complaints,
                color_continuous_scale=['red','green','blue']
                )

viz_tree.update_layout(title_font_size=16,title_font_family='Times New Roman')

with st.container():
	col1, col2= st.columns([1,1])
	col1.plotly_chart(viz_complaints_by_product, use_container_width=True)
	col2.plotly_chart(viz_complaints_over_time, use_container_width=True)

with st.container():
	col3, col4= st.columns([1,1])
	col3.plotly_chart(viz_complaints_by_channel, use_container_width=True)
	col4.plotly_chart(viz_tree,use_container_width=True)
    

# ---- HIDE STREAMLIT STYLE ----
hide_st_style =  """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)