import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#------Importing the trade data------
trade_data_lk = pd.read_excel('trade_lka.xlsx')

#------Preprocessing the data------
#Removing unnecessary columns
trade_data_lk.drop(columns=[ 'Indicator Code', 'Country Name','Country ISO3'], inplace=True)
#hecking Data Types
print(trade_data_lk.dtypes )#Rounding Value column to 2 decimal places
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
print(trade_data_lk['Indicator Name'])

trade_data_lk['Indicator Name'] = trade_data_lk['Indicator Name'].replace(indicator_rename)
#Pivoting the data to have 'Year' as index and 'Indicator Name' as columns
trade_data_lk = trade_data_lk.pivot(index='Year', columns='Indicator Name', values='Value').copy()
trade_data_lk.reset_index(inplace=True)
print(trade_data_lk)
    
#Removing NaN values from the dataset by removing rows with NaN values
trade_data_lk.isnull().sum()
trade_data_lk['Year'] = pd.to_numeric(trade_data_lk['Year'], errors='coerce')
trade_data_lk = trade_data_lk.dropna(subset=['Year'])
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
print(trade_data_lk.dtypes)
print(trade_data_lk.shape)

#------Initial Dashboard Setup------
import streamlit as st
st.set_page_config(layout="wide")
st.title("How does Sri Lanka's foreign trade impact its economic sustainability?")

#------Sidebar Controls------
st.sidebar.header("Dashboard Controls")
global_year_range = st.sidebar.slider(
    'Select Year Range', 
    min_value=int(trade_data_lk['Year'].min()), 
    max_value=int(trade_data_lk['Year'].max()), 
    value=(int(trade_data_lk['Year'].min()), int(trade_data_lk['Year'].max())), 
    step=1
)
st.sidebar.divider() # Add a divider in the sidebar


# Filter data once for all visualizations
filtered_df = trade_data_lk[
    (trade_data_lk['Year'] >= global_year_range[0]) & 
    (trade_data_lk['Year'] <= global_year_range[1])
]

# Setup the Tabs
tab_macro, tab_partners, tab_metrics , tab_dataset = st.tabs([
    "Macroeconomic Trends", 
    "Partner Composition", 
    "Trade Metrics",
    "Dataset"
])

#------Macroeconomic Trends Tab------
with tab_macro:
    st.markdown("<h1 style='text-align: center;'>Macroeconomic Trends </h1>", unsafe_allow_html=True)    
    col1 , col2 = st.columns(2)
    with col1:
        #------Bar Chart: Exports and Imports of Goods & Services (Visualization No.1 (V1))------
        st.subheader(f"Import & Export Trends over time")

        v1_cols = ['Exports of Goods & Services (USD Billions)', 'Imports of Goods & Services (USD Billions)']
        if not filtered_df.empty and filtered_df[v1_cols].notna().any().any():
            st.bar_chart(
                filtered_df, 
                x='Year', 
                y=v1_cols,
                stack=False,
                y_label= 'USD($ Billions)',
            )
        else:
            st.info("Data for this period is not available.")
        st.divider() # Divider between V1 and V2 if they were in separate columns
    
    with col2:

        #------Bar Chart: Service Export Trends (Visualization No.2 (V2))------
            st.subheader("Service Export Composition Over Time")

            select_box_2 = st.selectbox("Select Service Export Indicators",
                options=[
                    'ICT service exports (% of service exports, BoP)',
                    'Travel services (% of service exports, BoP)',
                    'Transport services (% of commercial service exports)',
                    'Insurance and financial services (% of commercial service exports)',
                    'Computer, communications and other services (% of commercial service exports)'
                ]
            )

            st.write("You selected:", select_box_2)

            if not filtered_df.empty and filtered_df[select_box_2].notna().any():
                st.bar_chart(x='Year', y=[select_box_2], data=filtered_df)
            else:
                st.info("Data for this period is not available.")
    st.divider() # Divider after V2

        #------Partner Composition Tab------
with tab_partners:
    st.markdown("<h1 style='text-align: center;'>Sri Lanka's Trade Partner Composition</h1>", unsafe_allow_html=True)    


    #------Sunburst Diagram: Merchandise Export Composition (Visualization No.3(V3))------
    st.subheader("Merchandise Export Destinations Distribution")
    #Year selector 
    available_years_3 = sorted([y for y in filtered_df['Year'].unique() if y != 2024], reverse=True)
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
            val_series = filtered_df.loc[filtered_df['Year'] == selected_year_3, indicator]
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
            color='Level 1',
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No merchandise export data available for {selected_year_3}.")
    st.divider() # Divider after V3

#------Trade Metrics Tab------
with tab_metrics:
    st.markdown("<h1 style='text-align: center;'> Trade Metrics </h1>", unsafe_allow_html=True)    


    col4 , col5 = st.columns(2)
    #------Line Chart:Net barter terms of trade (Visualization No.4 (V4))------
    with col4:
        st.header("Net Barter Terms of Trade Over Time")
        # Define the column and threshold
        trade_col = 'Net barter terms of trade index (2015 = 100)'
        threshold = 100

        # Create the plot
        if not filtered_df.empty and filtered_df[trade_col].notna().any():
            fig = px.line(
                filtered_df, 
                x='Year', 
                y=trade_col
            )
            
            # Filter out rows where the trade_col value is NaN for robust plotting
            plot_data = filtered_df.dropna(subset=[trade_col]).copy()

            if not plot_data.empty:
                fig = go.Figure()

                x_data = plot_data['Year'].values
                y_data = plot_data[trade_col].values

                # Add fill traces (polygons) first to ensure they are behind the lines
                for i in range(len(x_data) - 1):
                    x1, y1 = x_data[i], y_data[i]
                    x2, y_data_next = x_data[i+1], y_data[i+1]

                    # Calculate intersection point if the line crosses the threshold
                    intersect_x = None
                    if (y1 > threshold and y_data_next < threshold) or \
                    (y1 < threshold and y_data_next > threshold):
                        if x2 == x1: # Should not happen with year data
                            intersect_x = x1
                        else:
                            slope = (y_data_next - y1) / (x2 - x1)
                            if slope != 0:
                                intersect_x = x1 + (threshold - y1) / slope
                            # If slope is 0 and it's crossing, it means it's a horizontal line at threshold,
                            # which is handled by the non-crossing cases or results in no fill.

                    # Case 1: Entire segment above or at threshold
                    if y1 >= threshold and y_data_next >= threshold:
                        fig.add_trace(go.Scatter(
                            x=[x1, x2, x2, x1],
                            y=[y1, y_data_next, threshold, threshold],
                            fill='toself',
                            fillcolor='rgba(0, 255, 0, 0.1)', # Light green
                            mode='none',
                            hoverinfo='skip',
                            showlegend=False
                        ))
                    # Case 2: Entire segment below or at threshold
                    elif y1 <= threshold and y_data_next <= threshold:
                        fig.add_trace(go.Scatter(
                            x=[x1, x2, x2, x1],
                            y=[y1, y_data_next, threshold, threshold],
                            fill='toself',
                            fillcolor='rgba(255, 0, 0, 0.1)', # Light red
                            mode='none',
                            hoverinfo='skip',
                            showlegend=False
                        ))
                    # Case 3: Segment crosses the threshold
                    elif intersect_x is not None:
                        if y1 > threshold: # Starts above, goes below
                            # Green part (from x1 to intersect_x)
                            fig.add_trace(go.Scatter(
                                x=[x1, intersect_x, intersect_x, x1],
                                y=[y1, threshold, threshold, y1],
                                fill='toself',
                                fillcolor='rgba(0, 255, 0, 0.1)',
                                mode='none',
                                hoverinfo='skip',
                                showlegend=False
                            ))
                            # Red part (from intersect_x to x2)
                            fig.add_trace(go.Scatter(
                                x=[intersect_x, x2, x2, intersect_x],
                                y=[threshold, y_data_next, threshold, threshold],
                                fill='toself',
                                fillcolor='rgba(255, 0, 0, 0.1)',
                                mode='none',
                                hoverinfo='skip',
                                showlegend=False
                            ))
                        else: # Starts below, goes above
                            # Red part (from x1 to intersect_x)
                            fig.add_trace(go.Scatter(
                                x=[x1, intersect_x, intersect_x, x1],
                                y=[y1, threshold, threshold, y1],
                                fill='toself',
                                fillcolor='rgba(255, 0, 0, 0.1)',
                                mode='none',
                                hoverinfo='skip',
                                showlegend=False
                            ))
                            # Green part (from intersect_x to x2)
                            fig.add_trace(go.Scatter(
                                x=[intersect_x, x2, x2, intersect_x],
                                y=[threshold, y_data_next, threshold, threshold],
                                fill='toself',
                                fillcolor='rgba(0, 255, 0, 0.1)',
                                mode='none',
                                hoverinfo='skip',
                                showlegend=False
                            ))

                # Add the main line (on top of fills)
                fig.add_trace(go.Scatter(
                    x=plot_data['Year'],
                    y=plot_data[trade_col],
                    mode='lines',
                    name='Net Barter Terms of Trade',
                    line=dict(color='blue', width=2),
                    hovertemplate='Year: %{x}<br>Value: %{y:.2f}<extra></extra>'
                ))

                # Add the threshold line (on top of fills)
                fig.add_trace(go.Scatter(
                    x=plot_data['Year'],
                    y=[threshold] * len(plot_data),
                    mode='lines',
                    name=f'Threshold ({threshold})',
                    line=dict(color='gray', dash='dash', width=1),
                    hoverinfo='skip'
                ))

                # Add dummy traces for legend entries for the fill areas
                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=10, color='rgba(0, 255, 0, 0.1)', symbol='square'),
                    name='Above 100 (Fill)',
                    hoverinfo='skip'
                ))
                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=10, color='rgba(255, 0, 0, 0.1)', symbol='square'),
                    name='Below 100 (Fill)',
                    hoverinfo='skip'
                ))

                fig.update_layout(
                    title="Net Barter Terms of Trade Over Time",
                    xaxis_title="Year",
                    yaxis_title=trade_col,
                    hovermode="x unified"
                )

                st.plotly_chart(fig)
            else:
                st.info("No valid data points for this period after removing NaNs.")
            st.divider() # Divider between V4 and V5 if they were in separate columns
            # Display in Streamlit
        else:
            st.info("Data for this period is not available.")

    with col5:
        # ------Tariff Rate Across The Years For All Products: Line Chart (Visualization No.5)------
        st.header("Tariff Rate Across The Years")
        import statsmodels.api as sm
        if not filtered_df.empty and filtered_df['Tariff rate, applied, weighted mean, all products (%)'].notna().any():
            fig_5 = px.scatter(
                filtered_df, 
                x='Year', 
                y='Tariff rate, applied, weighted mean, all products (%)',
                labels={
                    "Year": "Year",
                    "Tariff rate, applied, weighted mean, all products (%)":"Applied Tariff Rate (%)"},
                trendline="ols"
            )

            st.plotly_chart(fig_5)
        else:
            st.info("Data for this period is not available.")
    st.divider() # Divider after V5

with tab_dataset:

    st.markdown("<h1 style='text-align: center;'> Sri Lanka Trade Dataset Overview </h1>", unsafe_allow_html=True)    
    st.divider() # Divider after the header
    
    st.dataframe(filtered_df)
    st.download_button(
        label="Download Dataset as CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='sri_lanka_trade_data.csv',
        mime='text/csv'
    )