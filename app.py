import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

data = pd.read_csv("Atharva_MaterialDepot_tiles2_modififed.csv")

# Rename the 'tiles_Description' column to 'Description'
data.rename(columns={'tiles_Description': 'Description'}, inplace=True)

data['Category '] = data['Category '].str.strip()


# Remove leading/trailing whitespace from the column name 'Category '
data.rename(columns={'Category ': 'Category'}, inplace=True)

# Main function to run the recommendation system
def main():
    st.title("Material Recommendation System")

    # Collect user preferences
    selected_category = st.selectbox("Select preferred category (or leave blank for any): ", [''] + data['Category'].unique())
    
    # Filter brands based on selected category
    if selected_category:
        filtered_brands = data[data['Category'] == selected_category]['Brand_Name'].unique()
    else:
        filtered_brands = data['Brand_Name'].unique()

    selected_brand = st.selectbox("Select preferred brand (or leave blank for any): ", [''] + list(filtered_brands))
    
    preferences = {
        'Brand_Name': selected_brand,
        'Category': selected_category,
        'Price_Range': st.selectbox("Enter preferred price range", ['', 'Low', 'Medium', 'High'])
    }

    # Function to recommend items based on user preferences
    def recommend_items(preferences, data, top_n=5):
        recommendations = []

        # Filter data based on user preferences
        filtered_data = data.copy()
        if preferences['Brand_Name']:
            filtered_data = filtered_data[filtered_data['Brand_Name'] == preferences['Brand_Name']]
        if preferences['Category']:
            filtered_data = filtered_data[filtered_data['Category'] == preferences['Category']]
        if preferences['Price_Range']:
            price_range_map = {'Low': (0, 50), 'Medium': (50, 100), 'High': (100, float('inf'))}
            price_range = price_range_map[preferences['Price_Range']]
            filtered_data = filtered_data[(filtered_data['Price_Per_SqFt'] >= price_range[0]) &
                                          (filtered_data['Price_Per_SqFt'] < price_range[1])]

        # If no items match the preferences, return empty recommendations
        if filtered_data.empty:
            return recommendations

        # Select top_n items based on some criterion (e.g., descending Price_Per_SqFt)
        top_items = filtered_data.nlargest(top_n, 'Price_Per_SqFt')

        # Convert the top_items DataFrame to a list of dictionaries
        for index, row in top_items.iterrows():
            recommendation = {
                'Brand_Name': row['Brand_Name'],
                'Description': row['Description'],
                'Price_Per_SqFt': row['Price_Per_SqFt'],
                'Price_Per_Box': row['Price_Per_Box'],
                'Category': row['Category'],
                'Image_Link': row['Image_Link']  # Add the image URL to the recommendation
            }
            recommendations.append(recommendation)

        return recommendations

    # Recommend items based on user preferences
    recommendations = recommend_items(preferences, data)

    # Display recommendations
    st.subheader("Recommendations:")
    for item in recommendations:
        st.write("Brand Name:", item['Brand_Name'])
        st.write("Description:", item['Description'])
        st.write("Price Per SqFt:", item['Price_Per_SqFt'])
        st.write("Price Per Box:", item['Price_Per_Box'])
        st.write("Category:", item['Category'])
        st.image(item['Image_Link'], caption='Image Link', use_column_width=True)
        st.write("\n") # Add a newline for better readability

# Run the recommendation system
if __name__ == "__main__":
    main()

