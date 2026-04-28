# Sri Lanka Trade Sustainability Dashboard
This project is an interactive Streamlit dashboard that analyzes Sri Lanka’s trade data to evaluate economic sustainability trends. It provides visual insights into imports & export trends, merchandise trade partners & trade metrics (i.e: Net Barter Terms over Trade, Tarrif Rate) 

#------Deployment------
    # Clone the repository
    git clone <https://github.com/adeeb20241760/  Sri-Lanka-Trade-Sustainability-Dashboard-W2149472->

    # Navigate to project folder
    cd 
    Sri-Lanka-Trade-Sustainability-Dashboard-W2149472-

    # Install dependencies
    pip install -r requirements.txt

    # Run the app
    streamlit run app.py
#------Objectives------
	To collect and organise relevant economic data related to trade, imports, and services 
	To design and implement interactive visualisations using Streamlit 
	To enable user interaction through filters such as year range and indicator selection 
	To identify trends and patterns in service trade and imports over time 
	To evaluate the performance and usability of the dashboard through structured testing 
	To interpret how selected indicators relate to aspects of economic sustainability

#------Features------
    Year-wise filtering
    Trade Indicator-wise filtering
    Interactive charts

#------Dataset------
    Dataset Name: Trade Indicators for Sri Lanka
    Source: The Humanitarian Data Exchange
    Source Link: https://data.humdata.org/dataset/world-bank-trade-indicators-for-sri-lanka 

#------Data Cleaning------
    Removing unnecessary columns, 
    Rounding values to 2 decimal places, 
    currency values to be represented in billions (for easy readability), 
    Pivoting the dataset from wide to long format, 
    Finally removing null values

#------Issues------
    An issue occurred where dashboard visualisations failed to render due to invalid values in the Year column. The column contained missing (NaN) and non-numeric entries (e.g., "N/A", empty strings), which caused errors during integer conversion. 
        trade_data_lk.dropna(axis = 0, inplace=True) 
        was changed to:
        trade_data_lk['Year'] = pd.to_numeric(trade_data_lk['Year'], errors='coerce')
        trade_data_lk = trade_data_lk.dropna(subset=['Year'])
        While this did mean the visualisations could be rendered a re-check of null values revealed that there were null values in the dataset.
    


