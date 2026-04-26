import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#------Importing the trade data------
trade_data_lk = pd.read_excel('trade_lka.xlsx')

#------Preprocessing the data------
#Removing unnecessary columns
trade_data_lk.drop(columns=[ 'Indicator Code', 'Country Name','Country ISO3'], inplace=True)
#hecking Data Types
trade_data_lk.dtypes 
#Rounding Value column to 2 decimal places
trade_data_lk['Value'] = trade_data_lk['Value'].round(2)
#Dealing with large currency values
trade_data_lk.loc[trade_data_lk['Value'] > 1000, 'Value'] = trade_data_lk['Value'] / 1e9

indicator_rename = {
    'Exports of goods and services (BoP, current US$)': 'Exports of Goods & Services (USD Billions)',
    'Imports of goods and services (BoP, current US$)': 'Imports of Goods & Services (USD Billions)',
    'Exports of goods, services and primary income (BoP, current US$)': 'Exports of Goods, Services & Income (USD Billions)',
    'Imports of goods, services and primary income (BoP, current US$)': 'Imports of Goods, Services & Income (USD Billions)',
    'Goods exports (BoP, current US$)': 'Goods Exports (USD Billions)',
    'Goods imports (BoP, current US$)': 'Goods Imports (USD Billions)',
    'Service exports (BoP, current US$)': 'Service Exports (USD Billions)',
    'Service imports (BoP, current US$)': 'Service Imports (USD Billions)',
    'Net trade in goods and services (BoP, current US$)': 'Net Trade in Goods & Services (USD Billions)',
    'Net trade in goods (BoP, current US$)': 'Net Trade in Goods (USD Billions)',
    'ICT service exports (BoP, current US$)': 'ICT Service Exports (USD Billions)',

        
}
trade_data_lk['Indicator Name']

trade_data_lk['Indicator Name'] = trade_data_lk['Indicator Name'].replace(indicator_rename)
#Pivoting the data to have 'Year' as index and 'Indicator Name' as columns
trade_data_lk = trade_data_lk.pivot(index='Year', columns='Indicator Name', values='Value').copy()
trade_data_lk.reset_index(inplace=True)
print(trade_data_lk)
    
#Removing NaN values from the dataset by removing rows with NaN values
trade_data_lk.isnull().sum()
trade_data_lk.dropna(axis = 0, inplace=True)
trade_data_lk['Year'] = trade_data_lk['Year'].astype(int)

#------Testing------

#Checking for duplicates in the dataset
trade_data_lk.duplicated().any()

#Checking for negative values in the dataset
(trade_data_lk.select_dtypes(include=['float64', 'int64']) < 0).any()

#Checking for null values in the dataset
trade_data_lk.isnull().sum().any()

#Checking invalid Year values
trade_data_lk[~trade_data_lk['Year'].between(1960, 2024)].any()

#Checking invalid data types
trade_data_lk.dtypes

trade_data_lk.shape

#------Initial Dashboard Setup------
import streamlit as st
st.title("How does Sri Lanka's foreign trade impact its economic sustainability?")

#------Bar Chart: Exports and Imports of Goods & Services (Visualization No.1 (V1))------

year_range = st.slider(
    'Select Year Range', 
    min_value=int(trade_data_lk['Year'].min()), 
    max_value=int(trade_data_lk['Year'].max()), 
    value=(int(trade_data_lk['Year'].min()), int(trade_data_lk['Year'].max())), 
    step=1
)

filtered_data = trade_data_lk[
    (trade_data_lk['Year'] >= year_range[0]) & 
    (trade_data_lk['Year'] <= year_range[1])
]

st.subheader(f"Import & Export Trends from {year_range[0]} to {year_range[1]}")
st.bar_chart(
    filtered_data, 
    x='Year', 
    y=['Exports of Goods & Services (USD Billions)', 'Imports of Goods & Services (USD Billions)'],
    stack=False,
    y_label= 'USD($ Billions)',
)

#------Bar Chart: Service Export Trends (Visualization No.2 (V2))------
st.subheader("Service Export Composition Over Time")

year_range_2 = st.slider(
    'Select Year Range', 
    min_value=int(trade_data_lk['Year'].min()), 
    max_value=int(trade_data_lk['Year'].max()), 
    value=(int(trade_data_lk['Year'].min()), int(trade_data_lk['Year'].max())), 
    step=1,
    key = 'slider_2'
)

filtered_data_2 = trade_data_lk[
    (trade_data_lk['Year'] >= year_range_2[0]) & 
    (trade_data_lk['Year'] <= year_range_2[1])
]
select_box_2 = st.selectbox("Select Service Export Indicators",
    options=[
        'ICT service exports (% of service exports, BoP)',
        'Travel services (% of service exports, BoP)',
        'Transport services (% of commercial service exports)',,
        'Insurance and financial services (% of commercial service exports)',
        'Communications, computer, etc. (% of service exports, BoP)'
    ]
)

st.write("You selected:", select_box_2)

st.bar_chart(x='Year', y=[select_box_2], data=filtered_data_2)

#------Sunburst Diagram: Merchandise Export Composition (Visualization No.3(V3))------

#Year selector 
available_years_3 = sorted(trade_data_lk['Year'].unique(), reverse=True)

selected_year_3 = st.selectbox(
    "Select Year",
    options=available_years_3,
    key='sunburst_year'
)

#Building the dataframe
merch_indicators = {
    'Merchandise exports to high-income economies (% of total merchandise exports)':
        ('High-Income Countries', 'High-Income Countries', 'High-Income Countries'),

    'Merchandise exports to low- and middle-income economies in East Asia & Pacific (% of total merchandise exports)':
        ('Low/Middle Income Countries', 'Outside Region', 'East Asia & Pacific'),

    'Merchandise exports to low- and middle-income economies in Europe & Central Asia (% of total merchandise exports)':
        ('Low/Middle Income Countries', 'Outside Region', 'Europe & Central Asia'),

    'Merchandise exports to low- and middle-income economies in Latin America & the Caribbean (% of total merchandise exports)':
        ('Low/Middle Income Countries', 'Outside Region', 'Latin America & Caribbean'),

    'Merchandise exports to low- and middle-income economies in Middle East & North Africa (% of total merchandise exports)':
        ('Low/Middle Income Countries', 'Outside Region', 'Middle East & North Africa'),

    'Merchandise exports to low- and middle-income economies in Sub-Saharan Africa (% of total merchandise exports)':
        ('Low/Middle Income Countries', 'Outside Region', 'Sub-Saharan Africa'),

    'Merchandise exports to low- and middle-income economies in South Asia (% of total merchandise exports)':
        ('Low/Middle Income Countries', 'Inside Region', 'South Asia'),

    'Merchandise exports by the reporting economy, residual (% of total merchandise exports)':
        ('Other (Residual)', 'Other (Residual)', 'Other (Residual)'),
}
rows = []
for indicator, (level1, level2, level3) in merch_indicators.items():
    if indicator in trade_data_lk.columns:
        val_series = trade_data_lk.loc[trade_data_lk['Year'] == selected_year_3, indicator]
        if not val_series.empty:
            rows.append({
                'Level 1': level1,
                'Level 2': level2,
                'Level 3': level3,
                'Value': val_series.values[0]
            })

    sunburst_df = pd.DataFrame(rows)

#Drawing the sunburst chart 
if not sunburst_df.empty:
    fig = px.sunburst(
        sunburst_df,
        path=['Level 1', 'Level 2', 'Level 3'],
        values='Value',
        title=f'Merchandise Export Destinations — {selected_year_3}',
        color='Level 1',
    )
    st.subheader("Merchandise Export Destinations Distribution")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"No merchandise export data available for {selected_year_3}.")
