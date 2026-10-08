import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import math
import urllib.parse
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Smart City Parking Tracker",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATABASE_NAME = "parking.db"


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            total_spaces INTEGER NOT NULL,
            occupied_spaces INTEGER NOT NULL,
            price_per_hour REAL NOT NULL,
            opening_time TEXT NOT NULL,
            closing_time TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# SAMPLE DATA
# ============================================================

def insert_sample_data():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM parking_lots")

    count = cursor.fetchone()[0]

    if count == 0:

        sample_data = [

            (
                "Connaught Place Parking",
                "Connaught Place",
                28.6315,
                77.2167,
                300,
                210,
                40,
                "06:00",
                "23:00"
            ),

            (
                "India Gate Parking",
                "India Gate",
                28.6129,
                77.2295,
                200,
                95,
                30,
                "05:00",
                "23:00"
            ),

            (
                "Karol Bagh Metro Parking",
                "Karol Bagh",
                28.6448,
                77.1905,
                250,
                180,
                25,
                "06:00",
                "22:30"
            ),

            (
                "Rajiv Chowk Parking",
                "Rajiv Chowk",
                28.6328,
                77.2197,
                400,
                360,
                50,
                "05:30",
                "23:30"
            ),

            (
                "Saket Mall Parking",
                "Saket",
                28.5287,
                77.2160,
                500,
                275,
                60,
                "10:00",
                "23:00"
            ),

            (
                "Lajpat Nagar Central Parking",
                "Lajpat Nagar",
                28.5706,
                77.2430,
                350,
                140,
                35,
                "06:00",
                "22:00"
            ),

            (
                "Nehru Place Parking",
                "Nehru Place",
                28.5494,
                77.2501,
                450,
                405,
                45,
                "07:00",
                "23:00"
            ),

            (
                "Dwarka Sector 10 Parking",
                "Dwarka",
                28.5823,
                77.0586,
                300,
                120,
                30,
                "06:00",
                "22:00"
            ),

            (
                "Noida Sector 18 Parking",
                "Noida Sector 18",
                28.5708,
                77.3260,
                600,
                420,
                50,
                "06:00",
                "23:30"
            ),

            (
                "Vasant Kunj Parking",
                "Vasant Kunj",
                28.5206,
                77.1570,
                250,
                75,
                35,
                "07:00",
                "22:00"
            )
        ]

        current_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        for item in sample_data:

            cursor.execute("""
                INSERT INTO parking_lots
                (
                    name,
                    location,
                    latitude,
                    longitude,
                    total_spaces,
                    occupied_spaces,
                    price_per_hour,
                    opening_time,
                    closing_time,
                    last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item[0],
                item[1],
                item[2],
                item[3],
                item[4],
                item[5],
                item[6],
                item[7],
                item[8],
                current_time
            ))

    conn.commit()
    conn.close()


# ============================================================
# LOAD DATA
# ============================================================

def load_parking_data():

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM parking_lots ORDER BY name",
        conn
    )

    conn.close()

    return df


# ============================================================
# UPDATE PARKING
# ============================================================

def update_occupied_spaces(
    parking_id,
    occupied_spaces
):

    conn = get_connection()
    cursor = conn.cursor()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        UPDATE parking_lots
        SET occupied_spaces = ?,
            last_updated = ?
        WHERE id = ?
    """, (
        occupied_spaces,
        current_time,
        parking_id
    ))

    conn.commit()
    conn.close()


# ============================================================
# ADD PARKING
# ============================================================

def add_parking_lot(
    name,
    location,
    latitude,
    longitude,
    total_spaces,
    occupied_spaces,
    price_per_hour,
    opening_time,
    closing_time
):

    conn = get_connection()
    cursor = conn.cursor()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO parking_lots
        (
            name,
            location,
            latitude,
            longitude,
            total_spaces,
            occupied_spaces,
            price_per_hour,
            opening_time,
            closing_time,
            last_updated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        location,
        latitude,
        longitude,
        total_spaces,
        occupied_spaces,
        price_per_hour,
        opening_time,
        closing_time,
        current_time
    ))

    conn.commit()
    conn.close()


# ============================================================
# DISTANCE
# ============================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    radius = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return radius * c


# ============================================================
# TRAFFIC CALCULATION
# ============================================================

def calculate_traffic(occupancy):

    """
    Demo traffic model.

    IMPORTANT:
    This is not real-time road traffic.
    It is a demonstration based on parking-area demand.

    Later this function can be replaced by
    Google Maps / Mapbox / HERE traffic API.
    """

    if occupancy >= 90:

        return (
            "🔴 Heavy",
            "Heavy traffic"
        )

    elif occupancy >= 70:

        return (
            "🟡 Moderate",
            "Moderate traffic"
        )

    else:

        return (
            "🟢 Low",
            "Low traffic"
        )


# ============================================================
# GOOGLE MAPS DIRECTIONS
# ============================================================

def create_google_maps_direction_url(
    destination_lat,
    destination_lon
):

    destination = (
        f"{destination_lat},{destination_lon}"
    )

    url = (
        "https://www.google.com/maps/dir/?api=1"
        "&destination="
        +
        urllib.parse.quote(destination)
        +
        "&travelmode=driving"
    )

    return url


# ============================================================
# GOOGLE MAPS SEARCH URL
# ============================================================

def create_google_maps_location_url(
    latitude,
    longitude
):

    return (
        "https://www.google.com/maps/search/?api=1"
        "&query="
        +
        urllib.parse.quote(
            f"{latitude},{longitude}"
        )
    )


# ============================================================
# INITIALIZE
# ============================================================

initialize_database()
insert_sample_data()

df = load_parking_data()


# ============================================================
# PROCESS DATA
# ============================================================

if not df.empty:

    df["vacant_spaces"] = (
        df["total_spaces"]
        -
        df["occupied_spaces"]
    )

    df["occupancy_percentage"] = (
        df["occupied_spaces"]
        /
        df["total_spaces"]
        *
        100
    )

    traffic_results = df[
        "occupancy_percentage"
    ].apply(calculate_traffic)

    df["traffic"] = traffic_results.apply(
        lambda x: x[0]
    )

    df["traffic_description"] = traffic_results.apply(
        lambda x: x[1]
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🚗 Smart Parking")

st.sidebar.markdown(
    """
    ### Smart City Parking System

    Find available parking,
    monitor parking occupancy,
    check traffic conditions
    and navigate to your destination.
    """
)

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "🔎 Find Parking",
        "🗺️ Traffic & Map",
        "🧭 Directions",
        "🅿️ Parking Locations",
        "🔄 Update Parking",
        "➕ Add Parking",
        "📈 Analytics",
        "ℹ️ About"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.title("🚗 Smart City Parking Tracker")

    st.subheader(
        "Parking + Traffic Monitoring Dashboard"
    )

    if df.empty:

        st.warning(
            "No parking data available."
        )

    else:

        total_locations = len(df)

        total_spaces = int(
            df["total_spaces"].sum()
        )

        occupied = int(
            df["occupied_spaces"].sum()
        )

        vacant = int(
            df["vacant_spaces"].sum()
        )

        occupancy = (
            occupied /
            total_spaces *
            100
        )

        heavy_traffic = int(
            (
                df["traffic"] ==
                "🔴 Heavy"
            ).sum()
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "Parking Locations",
            total_locations
        )

        col2.metric(
            "Total Spaces",
            f"{total_spaces:,}"
        )

        col3.metric(
            "Occupied",
            f"{occupied:,}"
        )

        col4.metric(
            "Vacant",
            f"{vacant:,}"
        )

        col5.metric(
            "Heavy Traffic Areas",
            heavy_traffic
        )

        st.divider()

        st.subheader(
            "🅿️ Parking & Traffic Status"
        )

        result = df[
            [
                "name",
                "location",
                "total_spaces",
                "occupied_spaces",
                "vacant_spaces",
                "occupancy_percentage",
                "traffic"
            ]
        ].copy()

        result["occupancy_percentage"] = (
            result["occupancy_percentage"]
            .round(1)
        )

        result.columns = [
            "Parking",
            "Location",
            "Total",
            "Occupied",
            "Vacant",
            "Occupancy %",
            "Traffic"
        ]

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "📍 Parking Map"
        )

        st.map(
            df,
            latitude="latitude",
            longitude="longitude"
        )


# ============================================================
# FIND PARKING
# ============================================================

elif page == "🔎 Find Parking":

    st.title("🔎 Find Available Parking")

    if df.empty:

        st.warning(
            "No parking locations available."
        )

    else:

        search = st.text_input(
            "Search area",
            placeholder="Example: Connaught Place"
        )

        minimum_vacant = st.slider(
            "Minimum vacant spaces",
            0,
            int(df["total_spaces"].max()),
            10
        )

        filtered = df[
            df["vacant_spaces"] >=
            minimum_vacant
        ]

        if search:

            filtered = filtered[
                filtered["name"].str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                filtered["location"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.subheader(
            f"{len(filtered)} parking locations found"
        )

        for _, row in filtered.iterrows():

            with st.container(border=True):

                col1, col2, col3, col4 = st.columns(4)

                col1.write(
                    f"### 🅿️ {row['name']}"
                )

                col1.write(
                    f"📍 {row['location']}"
                )

                col2.metric(
                    "Vacant",
                    f"{int(row['vacant_spaces'])}"
                )

                col3.metric(
                    "Occupancy",
                    f"{row['occupancy_percentage']:.1f}%"
                )

                col4.write(
                    f"🚦 **Traffic**\n\n"
                    f"{row['traffic']}"
                )

                st.write(
                    f"💰 ₹{row['price_per_hour']}/hour"
                )

                maps_url = (
                    create_google_maps_direction_url(
                        row["latitude"],
                        row["longitude"]
                    )
                )

                st.link_button(
                    "🧭 Get Directions",
                    maps_url
                )


# ============================================================
# TRAFFIC AND MAP
# ============================================================

elif page == "🗺️ Traffic & Map":

    st.title("🗺️ Traffic & Parking Map")

    st.info(
        "Traffic shown in this version is a demo traffic "
        "indicator based on parking-area occupancy. "
        "For true live road traffic, connect a traffic API."
    )

    if not df.empty:

        # ----------------------------------------------------
        # TRAFFIC FILTER
        # ----------------------------------------------------

        traffic_filter = st.multiselect(
            "Filter traffic",
            [
                "🟢 Low",
                "🟡 Moderate",
                "🔴 Heavy"
            ],
            default=[
                "🟢 Low",
                "🟡 Moderate",
                "🔴 Heavy"
            ]
        )

        traffic_df = df[
            df["traffic"].isin(
                traffic_filter
            )
        ]

        # ----------------------------------------------------
        # MAP
        # ----------------------------------------------------

        st.subheader(
            "📍 Parking Locations"
        )

        st.map(
            traffic_df,
            latitude="latitude",
            longitude="longitude"
        )

        st.divider()

        # ----------------------------------------------------
        # TRAFFIC TABLE
        # ----------------------------------------------------

        st.subheader(
            "🚦 Area Traffic Conditions"
        )

        traffic_table = traffic_df[
            [
                "name",
                "location",
                "traffic",
                "traffic_description",
                "vacant_spaces",
                "occupancy_percentage"
            ]
        ].copy()

        traffic_table[
            "occupancy_percentage"
        ] = traffic_table[
            "occupancy_percentage"
        ].round(1)

        traffic_table.columns = [
            "Parking",
            "Area",
            "Traffic",
            "Condition",
            "Vacant Spaces",
            "Occupancy %"
        ]

        st.dataframe(
            traffic_table,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# DIRECTIONS
# ============================================================

elif page == "🧭 Directions":

    st.title("🧭 Parking Navigation")

    st.write(
        "Select a parking location and get driving directions."
    )

    if df.empty:

        st.warning(
            "No parking locations available."
        )

    else:

        selected_name = st.selectbox(
            "Select destination parking",
            df["name"].tolist()
        )

        selected = df[
            df["name"] == selected_name
        ].iloc[0]

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                f"🅿️ {selected['name']}"
            )

            st.write(
                f"📍 **Area:** "
                f"{selected['location']}"
            )

            st.write(
                f"🟢 **Vacant:** "
                f"{int(selected['vacant_spaces'])} spaces"
            )

            st.write(
                f"🚦 **Traffic:** "
                f"{selected['traffic']}"
            )

            st.write(
                f"💰 **Price:** "
                f"₹{selected['price_per_hour']}/hour"
            )

        with col2:

            st.subheader(
                "📍 Destination"
            )

            st.write(
                f"Latitude: "
                f"{selected['latitude']}"
            )

            st.write(
                f"Longitude: "
                f"{selected['longitude']}"
            )

            location_url = (
                create_google_maps_location_url(
                    selected["latitude"],
                    selected["longitude"]
                )
            )

            direction_url = (
                create_google_maps_direction_url(
                    selected["latitude"],
                    selected["longitude"]
                )
            )

            st.link_button(
                "🗺️ Open Location in Google Maps",
                location_url
            )

            st.link_button(
                "🚗 Start Driving Directions",
                direction_url
            )

        st.divider()

        st.subheader(
            "🗺️ Destination Map"
        )

        destination_df = pd.DataFrame({
            "latitude": [
                selected["latitude"]
            ],
            "longitude": [
                selected["longitude"]
            ]
        })

        st.map(
            destination_df,
            latitude="latitude",
            longitude="longitude"
        )

        st.success(
            "Click 'Start Driving Directions' to open "
            "the route in Google Maps."
        )


# ============================================================
# PARKING LOCATIONS
# ============================================================

elif page == "🅿️ Parking Locations":

    st.title("🅿️ Parking Locations")

    if df.empty:

        st.warning(
            "No parking locations."
        )

    else:

        display_df = df[
            [
                "id",
                "name",
                "location",
                "total_spaces",
                "occupied_spaces",
                "vacant_spaces",
                "occupancy_percentage",
                "traffic",
                "price_per_hour",
                "last_updated"
            ]
        ].copy()

        display_df[
            "occupancy_percentage"
        ] = display_df[
            "occupancy_percentage"
        ].round(1)

        display_df.columns = [
            "ID",
            "Parking",
            "Location",
            "Total",
            "Occupied",
            "Vacant",
            "Occupancy %",
            "Traffic",
            "Price/Hour",
            "Last Updated"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader(
            "🗺️ Map"
        )

        st.map(
            df,
            latitude="latitude",
            longitude="longitude"
        )


# ============================================================
# UPDATE PARKING
# ============================================================

elif page == "🔄 Update Parking":

    st.title(
        "🔄 Update Parking Availability"
    )

    if df.empty:

        st.warning(
            "No parking locations."
        )

    else:

        selected_name = st.selectbox(
            "Parking Location",
            df["name"].tolist()
        )

        selected = df[
            df["name"] == selected_name
        ].iloc[0]

        st.write(
            f"Total spaces: "
            f"**{int(selected['total_spaces'])}**"
        )

        st.write(
            f"Current occupied: "
            f"**{int(selected['occupied_spaces'])}**"
        )

        new_occupied = st.number_input(
            "New occupied spaces",
            min_value=0,
            max_value=int(
                selected["total_spaces"]
            ),
            value=int(
                selected["occupied_spaces"]
            )
        )

        if st.button(
            "🔄 Update",
            type="primary"
        ):

            update_occupied_spaces(
                int(selected["id"]),
                int(new_occupied)
            )

            st.success(
                "Parking status updated."
            )

            st.rerun()


# ============================================================
# ADD PARKING
# ============================================================

elif page == "➕ Add Parking":

    st.title(
        "➕ Add Parking Location"
    )

    with st.form(
        "parking_form"
    ):

        name = st.text_input(
            "Parking Name"
        )

        location = st.text_input(
            "Location / Area"
        )

        col1, col2 = st.columns(2)

        with col1:

            latitude = st.number_input(
                "Latitude",
                value=28.6139,
                format="%.6f"
            )

        with col2:

            longitude = st.number_input(
                "Longitude",
                value=77.2090,
                format="%.6f"
            )

        total_spaces = st.number_input(
            "Total Spaces",
            min_value=1,
            value=100
        )

        occupied_spaces = st.number_input(
            "Occupied Spaces",
            min_value=0,
            value=0
        )

        price = st.number_input(
            "Price per Hour",
            min_value=0.0,
            value=30.0
        )

        opening = st.text_input(
            "Opening Time",
            value="06:00"
        )

        closing = st.text_input(
            "Closing Time",
            value="23:00"
        )

        submit = st.form_submit_button(
            "➕ Add Parking",
            type="primary"
        )

        if submit:

            if not name.strip():

                st.error(
                    "Enter parking name."
                )

            elif not location.strip():

                st.error(
                    "Enter location."
                )

            elif occupied_spaces > total_spaces:

                st.error(
                    "Occupied spaces cannot exceed total."
                )

            else:

                add_parking_lot(
                    name,
                    location,
                    latitude,
                    longitude,
                    total_spaces,
                    occupied_spaces,
                    price,
                    opening,
                    closing
                )

                st.success(
                    "Parking added successfully!"
                )

                st.rerun()


# ============================================================
# ANALYTICS
# ============================================================

elif page == "📈 Analytics":

    st.title(
        "📈 Parking & Traffic Analytics"
    )

    if not df.empty:

        # Occupancy

        fig1 = px.bar(
            df,
            x="name",
            y="occupancy_percentage",
            title="Parking Occupancy"
        )

        fig1.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        # Vacant

        fig2 = px.bar(
            df.sort_values(
                "vacant_spaces",
                ascending=False
            ),
            x="name",
            y="vacant_spaces",
            title="Available Parking Spaces"
        )

        fig2.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # Traffic distribution

        traffic_counts = (
            df["traffic"]
            .value_counts()
            .reset_index()
        )

        traffic_counts.columns = [
            "Traffic",
            "Locations"
        ]

        fig3 = px.pie(
            traffic_counts,
            names="Traffic",
            values="Locations",
            title="Traffic Distribution"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )


# ============================================================
# ABOUT
# ============================================================

elif page == "ℹ️ About":

    st.title(
        "ℹ️ About Smart City Parking Tracker"
    )

    st.markdown("""
    ## 🚗 Smart City Parking Tracker

    This project aims to reduce the time drivers spend
    searching for parking spaces.

    ### Current Features

    - Parking availability monitoring
    - Parking occupancy tracking
    - Vacant-space finder
    - Traffic status
    - Parking map
    - Google Maps navigation
    - Distance calculation support
    - Parking analytics
    - SQLite database

    ### Future Features

    The system can be upgraded with:

    - Real-time IoT parking sensors
    - GPS tracking
    - Live traffic APIs
    - Computer vision
    - Machine learning
    - Parking demand prediction
    - Dynamic pricing
    - Mobile application
    - User accounts
    - Online parking reservation

    ### AI/ML Component

    Historical data can be used to predict:

    - Parking demand
    - Future occupancy
    - Peak parking hours
    - Traffic patterns
    - Best parking location

    Example:

    "Rajiv Chowk parking is expected to become
    95% occupied between 6 PM and 7 PM."

    The application can then recommend an alternative
    parking location.
    """)


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "Smart City Parking Tracker v2.0"
)

st.sidebar.caption(
    "Python • Streamlit • SQLite • Pandas • Plotly"
)