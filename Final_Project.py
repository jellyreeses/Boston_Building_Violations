"""
Name:       Jordan Tandjung
CS230:      Section 2
Data:       Boston Building Violations
URL:        Link to your web application on Streamlit Cloud (if posted)


Description:

This program ... (a few sentences about your program and the queries and charts)
"""


import csv
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
from PIL import Image

st.title("Building Violations in Boston")
st.divider()
image = Image.open('Boston_Houses.jpg')
st.image(image, width=700)
st.divider()

BUILDING_VIOLATION = "Building Violations.csv"

dfBuild = pd.read_csv(BUILDING_VIOLATION, index_col="status")
dfFocused = dfBuild.filter(items = ['status_dttm','case_no','description','violation_city','violation_zip','latitude','longitude'])
dfFocused["Year"] = dfFocused["status_dttm"].astype(str).str[:4]
dfyearstreetsample = dfFocused[(dfFocused.Year == "2020") | (dfFocused.Year == "2021") | (dfFocused.Year == "2022") | (dfFocused.Year == "2023")]
dfyearsample = dfFocused[(dfFocused.Year == "2020") | (dfFocused.Year == "2021") | (dfFocused.Year == "2022") | (dfFocused.Year == "2023")]

count = dfyearsample.pivot_table(values = "case_no", index = "description", aggfunc="count")

dfCount = count.reset_index()
dfover100 = dfCount[(dfCount['case_no'] >= 100)]
dfunder100 = dfCount[(dfCount['case_no'] < 100)]
sum_under100 = dfunder100.sum()

new_row = {'description': 'Other', 'case_no': 470}
new_df = pd.concat([dfover100, pd.DataFrame([new_row])], ignore_index=True)
renamed = new_df.rename(columns={"description": "Type", "case_no": "Number"})
under_renamed = dfunder100.rename(columns={"description": "Type", "case_no": "Amount"})
dfbar = renamed.copy()
dfbar['Type'].replace('Failed to comply w permit term', 'Failed to Comply With Permit Term', inplace=True)
dfbar['Type'] = dfbar['Type'].replace("&", 'and', regex=True)
# dfbar['Type'] = dfbar['Type'].astype(float)
# dfbar.set_index('Type', inplace=True)

st.title("General Statistical Data")

selected_chart = st.selectbox("Please select a chart",["Please Select","Most Common Violations Bar Chart",
                                                       "Other Violations Bar Chart",
                                                       "Overall Violations Pie Chart",
                                                       "Number of Violations Per Year"])
if selected_chart == "Most Common Violations Bar Chart":
    frequency = dfbar.iloc[0:7, 0]
    typedesc = dfbar.iloc[0:7, 1]
    fig,ax = plt.subplots()
    plt.barh(frequency, typedesc, color="blue",height = .5)
    plt.title("Number of Building Violations By Type (2020-2023)")
    plt.xlabel("Frequency")
    plt.ylabel("Types of Violations")
    plt.legend(labels = ["Frequency of Violation"])
    st.pyplot(fig)
    st.write(dfbar.T)
    st.success("The most common types of building violations in the Boston area are:"
               "\n- Unsafe and Dangerous"
               "\n- Unsafe Structures"
               "\n- Testing and Certification"
               "\n- Maintenance"
               "\n- Failure to Obtain Permit"
               "\n- Failure to Comply With Permit Term")
elif selected_chart == "Other Violations Bar Chart":
    frequency = dfunder100.iloc[0:97, 0]
    typedesc = dfunder100.iloc[0:97, 1]
    fig, ax = plt.subplots()
    plt.bar(frequency, typedesc, color = "green")
    plt.xticks([])
    plt.title("Number of Building Violations By Type (2020-2023)")
    plt.ylabel("Frequency")
    plt.legend(labels=["Frequency of Violation"])
    st.pyplot(fig)
    st.write(under_renamed.T)
    st.success("There is a total number of 470 building violations in the Other category.")
elif selected_chart == "Overall Violations Pie Chart":
    fig, ax = plt.subplots()
    frequency = dfbar.iloc[0:7, 0]
    typedesc = dfbar.iloc[0:7, 1]
    ax.pie(typedesc,explode = (0, 0, 0, 0, 0, 0, 0.1), labels=frequency, autopct='%1.1f%%',
           shadow={'ox': -0.04, 'edgecolor': 'none', 'shade': 0.9}, startangle=195)
    st.pyplot(fig)
    st.success("The 'Failure to Obtain Permit' violation is the most common, making up 30% of all violations in a span of"
               " four years while the 'Failure to Comply With Permit Term' is the least common, making up 3.5% of all "
               "violations in the four year span.")
elif selected_chart == "Number of Violations Per Year":
    dfyear2020 = dfFocused[(dfFocused.Year == "2020")]
    amount_2020 = len(dfyear2020.index)
    dfyear2021 = dfFocused[(dfFocused.Year == "2021")]
    amount_2021 = len(dfyear2021.index)
    dfyear2022 = dfFocused[(dfFocused.Year == "2022")]
    amount_2022 = len(dfyear2022.index)
    dfyear2023 = dfFocused[(dfFocused.Year == "2023")]
    amount_2023 = len(dfyear2023.index)
    amounts = [amount_2020, amount_2021, amount_2022, amount_2023]
    years = ["2020", "2021", "2022", "2023"]
    mline, ax = plt.subplots()
    ax.plot(years, amounts, color='blue', linestyle =":", marker = ".")
    plt.xlabel("Years")
    plt.ylabel("Amount of Violations")
    plt.legend(labels =["Number of Violations That Year"])
    ax.set_ylim(ymin=500, ymax=1000)
    st.pyplot(mline)
    st.write("There was a total of:"
             "\n", amount_2020,"violations recorded in 2020,"
             "\n", amount_2021,"violations recorded in 2021,"
             "\n", amount_2022,"violations recorded in 2022,"
             "\n","and", amount_2023,"violations recorded in 2023. The biggest increase was from 2021 to 2022 and the "
                                     "biggest decrease was from 2022 to 2023.")
else:
    "Please Select a Chart"

st.divider()

st.write("\n")

def map(dataframe):
    view_state = pdk.ViewState(
        latitude=dataframe["latitude"].mean(),  # The latitude of the view center
        longitude=dataframe["longitude"].mean(),  # The longitude of the view center
        zoom=11,  # View zoom level
        pitch=35
    )
    # Create a map layer with the given coordinates
    layer1 = pdk.Layer(type='ScatterplotLayer',  # layer type
                       data=dataframe,  # data source
                       get_position='[longitude, latitude]',  # coordinates
                       get_radius=60,  # scatter radius
                       get_color=[0, 0, 0],  # scatter color
                       pickable=True  # work with tooltip
                       )
    layer2 = pdk.Layer('ScatterplotLayer',
                       data=dataframe,
                       get_position='[longitude, latitude]',
                       get_radius=50,
                       get_color=[255, 0, 0],
                       pickable=True
                       )
    # stylish tool tip: https://pydeck.gl/tooltip.html?highlight=tooltip
    tool_tip = {"html": "Name:<br/> <b>{NAME}</b>",
                "style": {"backgroundColor": "pink",
                          "color": "white"}
                }

    # Create a map based on the view, layers, and tool tip
    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/outdoors-v11',
        # Go to https://docs.mapbox.com/api/maps/styles/ for more map styles
        initial_view_state=view_state,
        layers=[layer1, layer2],  # The following layer would be on top of the previous layers
        tooltip=tool_tip
    )
    return st.pydeck_chart(map)

def menu(df):
    df_menu = df.rename(columns={"longitude": "Longitude", "latitude": "Latitude",
                                           "violation_zip": "Zip Code", "violation_city": "City",
                                           "case_no": "Case Number", "status_dttm": "Date Reported",
                                           "description": "Type", "case_no": "Number"})
    df_menu['Type'].replace('Failed to comply w permit term', 'Failed to Comply With Permit Term', inplace=True)
    df_menu.index.names = ['Status']
    return df_menu


st.title("Location Visualization for Violation Types")
st.divider()
image = Image.open('Boston_Houses2.jpg')
st.image(image, width=700)
st.divider()
st.header("Select an Option to See the Location of Building Violations!")

selected_map = st.radio("Please select a map", ["Please select a violation variation",
                                                "Unsafe and Dangerous",
                                                "Unsafe Structures",
                                                "Testing and Certification",
                                                "Maintenance",
                                                "Failure to Obtain Permit",
                                                "Failure to Comply With Permit Term"])
if selected_map == "Unsafe and Dangerous":
    dfyearsample = dfFocused[(dfFocused.description == "Unsafe and Dangerous")]
    st.success("Unsafe and Dangerous")
    st.map(dfyearsample)
    map(dfyearsample)
    dfyearsample = menu(dfyearsample)
    st.write(dfyearsample)
elif selected_map == "Unsafe Structures":
    dfyearsample = dfFocused[(dfFocused.description == "Unsafe Structures")]
    st.success("Unsafe Structures")
    st.map(dfyearsample)
    map(dfyearsample)
    dfyearsample = menu(dfyearsample)
    st.write(dfyearsample)
elif selected_map == "Testing and Certification":
    dfyearsample = dfFocused[(dfFocused.description == "Testing & Certification")]
    st.success("Testing and Certification")
    st.map(dfyearsample)
    map(dfyearsample)
    dfyearsample = menu(dfyearsample)
    st.write(dfyearsample)
elif selected_map == "Maintenance":
    dfyearsample = dfFocused[(dfFocused.description == "Maintenance")]
    st.success("Maintenance")
    st.map(dfyearsample)
    map(dfyearsample)
    dfyearsample = menu(dfyearsample)
    st.write(dfyearsample)
elif selected_map == "Failure to Obtain Permit":
    dfyearsample = dfFocused[(dfFocused.description == "Failure to Obtain Permit")]
    st.success("Failure to Obtain Permit")
    st.map(dfyearsample)
    map(dfyearsample)
    dfyearsample = menu(dfyearsample)
    st.write(dfyearsample)
elif selected_map == "Failure to Comply With Permit Term":
    dfyearsample = dfFocused[(dfFocused.description == "Failed to comply w permit term")]
    st.success("Failure to Comply With Permit Term")
    st.map(dfyearsample)
    map(dfyearsample)
    dfyearsample = menu(dfyearsample)
    st.write(dfyearsample)
else:
    "Please Select an Option"


def read_DataFrame(filename = "Building Violations.csv"): #to read the csv default to the building violation csv
    buildings_file = open(filename, "r")
    file_reader = list(csv.DictReader(buildings_file))
    # print(file_reader)
    # print(len(file_reader))
    return file_reader

def name_list(file_reader): #to compile only the names
    name = []
    for building in file_reader:
        street = []
        if "2020" == building['status_dttm'][0:4]:
            street.append(building['violation_stno'])
            street.append(building['violation_street'])
            street.append(building['violation_suffix'].upper())
            street_name = " ".join(street)
            name.append(street_name)
        elif "2021" == building['status_dttm'][0:4]:
            street.append(building['violation_stno'])
            street.append(building['violation_street'])
            street.append(building['violation_suffix'].upper())
            street_name = " ".join(street)
            name.append(street_name)
        elif "2022" == building['status_dttm'][0:4]:
            street.append(building['violation_stno'])
            street.append(building['violation_street'])
            street.append(building['violation_suffix'].upper())
            street_name = " ".join(street)
            name.append(street_name)
        elif "2023" == building['status_dttm'][0:4]:
            street.append(building['violation_stno'])
            street.append(building['violation_street'])
            street.append(building['violation_suffix'].upper())
            street_name = " ".join(street)
            name.append(street_name)
        else:
            continue
    return name

def searchStreetNames(allStreetNames, inputs): #to see if the name exists in the data
    dataFrame = read_DataFrame(BUILDING_VIOLATION)
    if inputs != "Please type a name.":
        for StreetNames in allStreetNames:
            if StreetNames == inputs:
                st.error("This building has record of a violation.")
                templist = str(StreetNames).split()
                for street in dataFrame:
                    if templist[0] == street['violation_stno']:
                        if templist[1] == street['violation_street']:
                            st.write("The violation(s) recorded include:", street['description']+". Please refer to table for other possible violations")
                            break
                    else:
                        continue
                break
            if StreetNames == allStreetNames[-1]:
                st.success('The building is safe! There are no violations recorded.')
                break



def main():
    st.title("Building Violation Search Engine")
    st.divider()
    image = Image.open('Boston_Houses3.jpg')
    st.image(image, width=700)
    st.divider()
    st.header("Enter an address to see if it has any building violations!")
    dataFrame = read_DataFrame(BUILDING_VIOLATION)
    print(dataFrame)
    allStreetNames = name_list(dataFrame)
    print(allStreetNames)
    #getting user tex
    inputs = st.text_input("Please Enter the Name of the Street (*Case Sensitive - Example: 20 Preble ST*)", "Please type a name.")
    searchStreetNames(allStreetNames, inputs)

    dfFocused2 = dfBuild.filter(items=['violation_stno','violation_street','violation_suffix','status_dttm', 'case_no', 'description', 'violation_city', 'violation_zip', 'latitude', 'longitude'])
    dfFocused2["Year"] = dfFocused["status_dttm"].astype(str).str[:4]
    dfyearstreetsample = dfFocused2[(dfFocused.Year == "2020") | (dfFocused.Year == "2021") | (dfFocused.Year == "2022") | (dfFocused.Year == "2023")]
    st.write(dfyearstreetsample)

main()


# st.write(count)
# st.write(dfCount)
# st.write(dfover100)
# st.write(dfunder100)
# st.write(dfbar)
# st.write(sum_under100)
#
#
# ''' for the graph showing the relationship between building violations in a certain area/city, and the general income of
#  that area, I plan to iterate through both data sets and if the zipcodes match, I will put the matching zipcodes into
#  a separate dataframe which i will then be able to use for the graph'''
#
# ''' for the graph displaying the locations of certain types of violations on a map, I'm going to link it to a drop-down
# menu or radio buttons and link it to the map using ivan's code through if statements so that only certain dots show up
# that correspond to the type of violation chosen'''
#
# '''for the search engine to search whether a street or area has a violation, I'm going to create a search bar engine and
# display the dataframe underneath so they can see the number of different entries there are. If the street name/zipcode
# matches with one from the dataframe, a message will display with the type of violation present in that street, if not,
# it will display that there are no violations'''
#
