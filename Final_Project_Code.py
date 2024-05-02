"""
Class: CS230--Section 003 
Name: Liam McGuire
Description: Final Project
I pledge that I have completed the programming assignment 
independently. 
I have not copied the code from a student or any source.
I have not given my code to any student. 
"""
import pandas as pd
import streamlit as st
pip install folium
import folium  # Folium was not taught in class
import matplotlib.pyplot as plt

st.set_page_config(page_title="CS 230 Final Project")  # Naming the web page  Source 2
st.set_option('deprecation.showPyplotGlobalUse', False)  # Streamlit recommended this line to prevent a matplotlib popup


@st.cache_data
def load_data(file_path):  # I wanted to cache the data that way it wasn't taking forever to load everytime
    dataframe = pd.read_csv(file_path, low_memory=False)  # Source 3
    return dataframe


@st.cache_data(experimental_allow_widgets=True)  # Needed to add this because the download button was taking awhile to
# load and there was a pop I wanted to ignore, code was given in popup
def home(df):
    st.title("CS 230 Final Project")
    st.header("Car Crashes in Massachusetts during 2017")
    st.write("By Liam McGuire")
    st.image("homegif.gif")  # Source 8
    st.sidebar.write("Hello, in this streamlit website we are going to analyze the data of all car crashes in "
                     "Massachussets for the 2017 year.")
    st.sidebar.write("If you wish to download the data for yourself, see the button below.")

    csv_data = df.to_csv(index=False).encode('utf-8')  # Source 3, encode is needed inorder to transfer data
    st.sidebar.download_button(
        label="Download CSV",
        data=csv_data,
        file_name='car_crashes_data.csv',
        mime='text/csv'
    )  # Source 2


def create_map(df):
    st.title("Fatal Crashes Map by Month")
    selected_month = st.slider("Select Month", 1, 12, 1)  # [ST1]
    df['CRASH_DATE_TEXT'] = pd.to_datetime(df['CRASH_DATE_TEXT'])  # Source 3
    filtered_df = df[df['CRASH_DATE_TEXT'].dt.month == selected_month]  # [DA4]
    m = folium.Map(location=(42, -71), tiles=None)  # [VIZ4] Source 1
    folium.TileLayer("OpenStreetMap").add_to(m)
    for i, row in filtered_df.iterrows():  # [DA8] Source 3
        if (not pd.isna(row['LAT']) and not pd.isna(row['LON']) and
                (row['NUMB_FATAL_INJR'] > 0)):  # [DA5]
            popup = (f"<b>Town Name:</b> {row['CITY_TOWN_NAME']}<br>"
                     f"<b>Crash Time:</b> {row['CRASH_TIME']}<br>"
                     f"<b>Fatalities:</b> {row['NUMB_FATAL_INJR']}")  # Source 5
            if not pd.isna(row['SPEED_LIMIT']):
                popup += f"<br><b>Speed Limit:</b> {row['SPEED_LIMIT']}"
            match row['NUMB_FATAL_INJR']:
                case 1:
                    color = "green"
                case 2:
                    color = "blue"
                case 3:
                    color = "red"
                case 4:
                    color = "purple"
                case _:
                    color = "gray"
            folium.Marker([row['LAT'], row['LON']], popup=folium.Popup(popup, max_width=175),
                          icon=folium.Icon(icon="", color=color)).add_to(m)  # Source 1
    m.save("map.html")
    st.components.v1.html(open("map.html", "r").read(), width=700, height=500)  # ChatGPT wasn't able to get HTML to
    # render and had to ask
    st.sidebar.write("In our first visual we are examining the car crashes that resulted in fatalities, we are taking "
                     "these data points and plotting them on a map, where they occured. We are then changing the color "
                     "of the icon based on the how many fatalities occured. Click on an individual icon to learn more "
                     "about the crash.")
    st.sidebar.markdown('''Key: 
    \n:green[green] = 1 
    \n:blue[blue] = 2 
    \n:red[red] = 3 
    \n:violet[purple] = 4 
    \n:gray[grey] = 5+''')


def time(df):
    st.title("Histogram of Crash Times")
    df['CRASH_TIME'] = pd.to_datetime(df['CRASH_TIME']).dropna()  # Source 3
    hit_and_run_str = ""
    hit_and_run_only = st.toggle("Hit and Runs Only")
    if hit_and_run_only:
        df = df[df['HIT_RUN_DESCR'] == 'Yes, hit and run']  # [DA4]
        hit_and_run_str = "given it was a hit and run "
    counts, bins, _ = plt.hist(df['CRASH_TIME'].dt.hour, bins=24, alpha=.65, color='blue')  # [DA7] Source 4 alpha=width
    plt.xlabel('Hour of Day')
    plt.ylabel('Frequency')
    plt.title('Histogram of Crash Times')
    total_crashes = len(df)
    lower_time = int(st.number_input("Enter the starting hour", 0, 23))  # [ST2] Source 2
    upper_time = int(st.number_input("Enter the ending hour", 0, 23))
    crashes_between_times = sum(counts[lower_time:upper_time+1])
    probability = (crashes_between_times / total_crashes)*100
    st.write(f"The probability of a crash being between {lower_time}:00 and {upper_time}:59 {hit_and_run_str}is "
             f"{probability:.2f}%")
    plt.axvspan(lower_time, upper_time, color='red', alpha=0.3)  # Source 4
    st.pyplot()  # [VIZ1] Source 2
    st.sidebar.write('''This visual displays a histogram of crash times, showing the distribution of car crashes 
    throughout the day in military time. By entering hours in the input fields you can calculate the probability that 
    a given crash occurred in that time frame. The histogram will show the range of which you are calculating the 
    probability on highlighted in :red[red]. You can also toggle the graph so it only shows crashes that were hit and
    runs.''')


def district(df):
    st.title("Pie Chart of Crashes by Distric")
    district_data = df['DISTRICT_NUM'].dropna()
    district_data.value_counts().plot(kind='pie', autopct='%1.2f%%')  # Source 3
    plt.title("District Distribution")
    st.pyplot()  # [VIZ2]
    st.image("hwydistricts.png")  # Source 7
    st.sidebar.write("This visual is a pie chart showcasing the distribution of car crashes across the 6 "
                     "highway districts of Massachussetts. An image breaking down the state into it's districts can be "
                     "seen below the pie chart.")


def responder(df):
    st.title("Bar Chart of First Responders to a Crash Filtered by County")
    selected_county = st.multiselect("Select County", df['CNTY_NAME'].unique())  # [ST3] Source 2 & 3
    filtered_df = df[df['CNTY_NAME'].isin(selected_county)]  # [DA4]
    first_responders = filtered_df['POLC_AGNCY_TYPE_DESCR'].dropna()
    responder_counts = first_responders.value_counts()  # Source 3
    fig, ax = plt.subplots()  # Source 4
    bars = ax.bar(responder_counts.index, responder_counts)  # Source 4

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords='offset points',
                    ha='center', va='bottom')  # ChatGPT, I couldn't get the values to appear on the barchart for the
        # life of me

    ax.set_xlabel('First Responder Type')  # Source 4
    ax.set_ylabel('Frequency')
    ax.set_title('First Responder Distribution')
    ax.set_xticklabels(responder_counts.index, rotation=45)
    st.pyplot(fig)  # [VIZ3]
    st.sidebar.write("This bar chart shows the distribution of first responders to a crash by type within "
                     "selected counties. You can filter the data by choosing which counties. Each bar represents a "
                     "unique type of first responder, and each bar has precise counts on it.")


def thanks(df):
    st.title("Thank You")
    st.header("Sources")
    st.write("Code:"
             "\n1. https://python-visualization.github.io/folium/latest/reference.html"
             "\n2. https://docs.streamlit.io/develop/api-reference"
             "\n3. https://pandas.pydata.org/docs/reference/index.html"
             "\n4. https://matplotlib.org/stable/api/pyplot_summary.html"
             "\n5. https://www.w3schools.com/tags/tag_b.asp\n"
             "\nImages:\n"
             "\n6. https://www.1800law1010.com/blog/the-common-causes-and-physics-of-a-car-crash/#"
             "\n7. https://www.mass.gov/info-details/massgis-data-massdot-highway-districts"
             "\n8. https://gifdb.com/gif/toy-car-crash-exploded-fxg7nt5s6ecjjvza.html"
             )
    st.header("Questions?")
    st.sidebar.write("Link to my Streamlit Cloud:")
    st.sidebar.link_button("URL", "")  # Source 2


def sidebar(df):
    page_names_to_funcs = {
        "Home": home,
        "Map of Fatalities": create_map,
        "Time of Crashes": time,
        "District the Crash Occurred In": district,
        "Primary Responder to the Crash": responder,
        "Thank You": thanks
    }  # [PY5]
    st.sidebar.image("sidebarimage.jpg")  # Source 6
    page_name = st.sidebar.selectbox("Choose a Page", page_names_to_funcs.keys())  # [ST4]
    page_names_to_funcs[page_name](df)


def main():
    df = load_data("2017_Crashes.csv")
    sidebar(df)


if __name__ == "__main__":
    main()
