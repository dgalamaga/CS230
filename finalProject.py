"""
Name: Dan Galamaga
CS230: Section 6
Data: Fortune 500 Corporate Headquarters
URL: Link to your web application on Streamlit Cloud (if posted)

Description: This program takes the data about the Fortune 500 Companies' headquarters as well as profitability
metrics such as revenue and profits. It creates visualizations to look at locations, metrics in relation to location,
and provides and overall insight about these companies. There are also widgets that allow the user to customize the
visualizations.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# Load data from file with try/except to get correct file
# [PY3]
FILE = "fortune_500_hq.csv"
try:
    DATA = pd.read_csv(FILE)
except FileNotFoundError:
    st.error(f"The data file {FILE} was not found. Please make sure it is available.")

# CLEANING DATA
# [DA7] Drops unused columns
CLEAN_DATA = DATA.drop(['X', 'Y', 'OBJECTID', 'ADDRESS', 'ADDRESS2', 'CITY', 'ZIP',
                        'COUNTY', 'SOURCE', 'PRC', 'COUNTYFIPS', 'COMMENTS', 'WEBSITE'], axis=1)
CLEAN_DATA.index = CLEAN_DATA['FID']  # Sets new index column
# [DA1] Uses lambda to format names
CLEAN_DATA['NAME'] = CLEAN_DATA['NAME'].apply(lambda x: x.title())
# [DA9] Calculate expenses and add new column to df
CLEAN_DATA['EXPENSES'] = CLEAN_DATA['REVENUES'] - CLEAN_DATA['PROFIT']

# FUNCTIONS
# Map of Company Locations [MAP]
def plotCompanyLocations(data):
    st.subheader("Company Locations Map")
    map = px.scatter_mapbox(
        data, lat="LATITUDE", lon="LONGITUDE", hover_name="NAME",
        hover_data={"STATE": True, "REVENUES": True, "PROFIT": True, "LATITUDE": False, "LONGITUDE": False},
        zoom=2, color="STATE")
    map.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(map)

def getHeatMapData():
    mapData = DATA.groupby('STATE')[['NAME']].count().reset_index()
    mapData.rename(columns={'NAME': 'Company Count'}, inplace=True)
    return mapData

# Create heat map of data [MAP2]
def createHeatMap(data, color='plasma'): # I think this map is really cool! It's what lead me to use plotly too
    map = px.choropleth(data,
                        locations='STATE', locationmode='USA-states', scope='usa', color='Company Count',
                        color_continuous_scale=color, title='Fortune 500 Companies by State')
    map.update_layout(dragmode=False) # So it stays in place (useful because I am only looking at US)
    st.plotly_chart(map)

# Revenue vs profit scatterplot [VIZ1] [DA4] [PY1]
def plotRevenueVsProfit(data, stateFilter=None, companyFilter=None):
    if stateFilter: # checks if filters are in use or not and makes df of filters values if there is something there
        data = data[data['STATE'] == stateFilter]
    if companyFilter:
        data = data[data['NAME'].isin(companyFilter)]

    chart = px.scatter(
        data, x="REVENUES", y="PROFIT", hover_name="NAME",
        title=f"Revenue vs Profit Analysis ({stateFilter or 'All States'})",
        labels={"REVENUES": "Revenue (Millions)", "PROFIT": "Profit (Millions)"}
    )
    st.plotly_chart(chart)

# Employee vs revenue histogram [VIZ2]
def plotEmployeeRevenueHistogram(data, bin_size): # user can change how "wide" the bins are
    chart = px.histogram(
        data, x="EMPLOYEES", y="REVENUES", nbins=bin_size,
        title=f"Revenue Histogram by Employee Count",
        labels={"EMPLOYEES": "Employee Count", "REVENUES": "Revenue"}
    )
    chart.update_layout(yaxis_title="Sum of Revenues (Millions)")
    st.plotly_chart(chart)

# Pie charts - revenue by state vs count by state [VIZ3] [PY1]
def plotRevenueCountByState(data, selection=5):
    # Group data by state for revenue and count
    revenueData = data.groupby('STATE')['REVENUES'].sum().reset_index()
    countData = data.groupby('STATE')['NAME'].count().reset_index()

    # Sort and get top X states for revenue - user selects number of individual states
    # [DA2]
    topRevenue = revenueData.sort_values(by='REVENUES', ascending=False).head(selection)
    otherRevenue = revenueData.sort_values(by='REVENUES', ascending=False).iloc[selection:]['REVENUES'].sum()
    topRevenue = pd.concat([topRevenue, pd.DataFrame({'STATE': ['Other'], 'REVENUES': [otherRevenue]})])
        # combines df that was manipulated ("topRevenue") with new row that is just the sum of the remaining states

    # Sort and get top X states for count
    topCount = countData.sort_values(by='NAME', ascending=False).head(selection)
    otherCount = countData.sort_values(by='NAME', ascending=False).iloc[selection:]['NAME'].sum()
    topCount = pd.concat([topCount, pd.DataFrame({'STATE': ['Other'], 'NAME': [otherCount]})])

    # Create side-by-side columns for streamlit
    col1, col2 = st.columns(2)

    # Plot revenue by state using matplotlib
    with col1:
        st.subheader("Revenue by Top States")
        fig1, ax1 = plt.subplots()
        ax1.pie(topRevenue['REVENUES'], autopct='%1.1f%%')
        fig1.legend(title="State Key", labels=topRevenue['STATE'])
        st.pyplot(fig1)

    # Plot count by state
    with col2:
        st.subheader("Count by Top States")
        fig2, ax2 = plt.subplots()
        ax2.pie(topCount['NAME'], autopct='%1.1f%%')
        fig2.legend(title="State Key", labels=topCount['STATE'])
        st.pyplot(fig2)

# Rank vs profit scatterplot [VIZ4]
def plotRankVsProfit(data):
    chart = px.scatter(
        data, x="RANK", y="PROFIT", hover_name="NAME",
        title="Rank vs Profit Scatterplot",
        labels={"RANK": "Rank", "PROFIT": "Profit (Millions)"}
    )
    chart.update_traces(marker=dict(color='red'))  # Changes markers to red color -- had to look up documentation
    st.plotly_chart(chart)

# Function to get the data needed to plot top 10 largest by different metrics
# [DA3] [PY2]
def findTops(data):
    topRevenues = data.nlargest(10, 'REVENUES')
    topExpenses = data.nlargest(10, 'EXPENSES')
    topProfits = data.nlargest(10, 'PROFIT')
    return topRevenues, topExpenses, topProfits

# Bar chart for top 10 by metric [VIZ5]
def plotTopCompanies(metric, stats="PROFIT"):
    chart = px.bar(
        metric, x="NAME", y=stats, title=f"Top 10 Companies' {stats.capitalize()}",
        labels={"NAME": "Company", stats: f"{stats.capitalize()} in Millions"}
    )
    # Logic to change color of chart depending on what is being shown
    if stats == "PROFIT":
        chart.update_traces(marker=dict(color='green'))
    elif stats == "REVENUES":
        chart.update_traces(marker=dict(color='blue'))
    elif stats == "EXPENSES":
        chart.update_traces(marker=dict(color='red'))
    st.plotly_chart(chart)

# Main function to organize function calls
def main():
    st.title("Fortune 500 Companies Analysis")
    # [ST4]
    st.sidebar.title("Navigation")
    # Allows for different "pages" so only one chart/map shows depending on selection
    # [ST1]
    page = st.sidebar.radio("Select a Visualization", [
        "Company Locations Map", "Revenue vs Profit Analysis",
        "Employee vs Revenue Histogram", "Revenue and Count by State",
        "Rank vs Profit", "Top 10 Revenues, Expenses, and Profits"
    ])

# LOGIC FOR CHANGING PAGES
    # Map visualization
    if page == "Company Locations Map":
        choice = st.sidebar.radio("Select Type of Map", ["Normal", "Heat"])
        if choice == "Normal":
            plotCompanyLocations(CLEAN_DATA)
        else:
            mapData = getHeatMapData()
            # [ST1]
            theme = st.sidebar.selectbox("Choose a Color Theme", ["plasma", "rainbow", "mint", "thermal", "icefire"])
            createHeatMap(mapData, theme)

    # Revenue vs profit
    elif page == "Revenue vs Profit Analysis":
        state = st.sidebar.selectbox("Filter by State", ["All"] + list(CLEAN_DATA['STATE'].unique()))
        # [ST2]
        companies = st.sidebar.multiselect("Filter by Company", CLEAN_DATA['NAME'].unique())
        plotRevenueVsProfit(CLEAN_DATA, state if state != "All" else None, companies)

    # employee vs revenue
    elif page == "Employee vs Revenue Histogram":
        # Use select_slider to provide a range of options from Broad to Narrow, with intermediate values
        # [ST3]
        range_option = st.sidebar.select_slider(
            "Change Employee Range",
            options=["Broad", "Medium", "Detailed", "Narrow"],
            value="Medium"  # Default value
        )
        # Maps the selected option to a numeric value for bin size
        if range_option == "Broad":
            bin_size = 25  # Fewer bins for broader ranges
        elif range_option == "Medium":
            bin_size = 50  # Moderate bin size for medium-level detail
        elif range_option == "Detailed":
            bin_size = 125  # More bins for more detailed ranges
        elif range_option == "Narrow":
            bin_size = 250  # Most bins for highly detailed ranges

        # Plot histogram with selected bin size
        plotEmployeeRevenueHistogram(CLEAN_DATA, bin_size)

    # Pie charts
    elif page == "Revenue and Count by State":
        stateNumber = st.sidebar.slider("Select # of Individual States", 1, 10, 5)
        plotRevenueCountByState(CLEAN_DATA, stateNumber)

    # Rank vs profit
    elif page == "Rank vs Profit":
        plotRankVsProfit(CLEAN_DATA)

    # Top 10 revenues, expenses, and profits
    elif page == "Top 10 Revenues, Expenses, and Profits":
        st.header("Top 10 Companies by Metrics")

        # Get top 10 stats
        topRevenues, topExpenses, topProfits = findTops(CLEAN_DATA)
        # Uses dictionary to map selection to returned variables
        # [PY5]
        metrics = {
            "REVENUES": topRevenues,
            "EXPENSES": topExpenses,
            "PROFIT": topProfits
        }
        # Access items in dictionary
        type = st.sidebar.radio("Select Metric", metrics.keys())
        metric = metrics.get(type)
        plotTopCompanies(metric, type)

if __name__ == "__main__":
    main()


### OTHER NOTES ###
# I used this article to figure out the documentation for the choropleth map:
# https://towardsdatascience.com/simplest-way-of-creating-a-choropleth-map-by-u-s-states-in-python-f359ada7735e
# This is also what lead me to look into plotly more and its capabilities
# Figuring out documentation for plotly mainly just consisted of googling how to do something
# and had no one particular article other than the plotly website itself