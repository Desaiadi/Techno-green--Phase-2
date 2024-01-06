import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

# Load the dataset of 100 crops
data = pd.read_csv('path_to_your_dataset.csv')  # Replace with the path to your dataset

def get_lifespan(crop_name, dataset):
    crop_data = dataset[dataset['Crop'] == crop_name]
    return crop_data['Life_Span (days)'].values[0] if not crop_data.empty else None

def display_optimal_conditions(crop_name, dataset):
    crop_data = dataset[dataset['Crop'] == crop_name]
    if not crop_data.empty:
        print(f"\nOptimal Conditions for {crop_name}:")
        for column in crop_data.columns:
            print(f"{column}: {crop_data[column].values[0]}")
    else:
        print(f"Sorry, no data found for the crop {crop_name}.")

# Input: Crop name from the user
user_crop_name = input("Enter the name of the crop: ")

# Display optimal conditions for the selected crop
display_optimal_conditions(user_crop_name, data)

# Get the lifespan of the crop from the dataset
user_crop_lifespan = get_lifespan(user_crop_name, data)

if user_crop_lifespan is not None:
    # Generate irrigation schedule for the user's crop
    full_schedule = pd.DataFrame(columns=['Crop', 'Day', 'Water_Requirement_Crop', 'Water_Requirement_Greenhouse', 'Motor_Run_Time_Minutes'])
    day_range = np.array(range(1, user_crop_lifespan + 1), dtype=float)

    # Assume a linear increase in water requirements as the plant matures
    water_requirement_per_day = data[data['Crop'] == user_crop_name]['Water_Requirement (mm)'].values
    water_requirement_per_day_crop = water_requirement_per_day * (1 + day_range / float(user_crop_lifespan))

    crop_schedule = pd.DataFrame({
        'Crop': [user_crop_name] * user_crop_lifespan,
        'Day': day_range,
        'Water_Requirement_Crop': water_requirement_per_day_crop,
        'Water_Requirement_Greenhouse': water_requirement_per_day_crop * 0.001 * 17 * 14  # Area of the greenhouse in square meters
    })

    # Calculate motor run time in minutes
    motor_flow_rate = 1.0  # Motor flow rate in liters per hour (adjust as needed)
    crop_schedule['Motor_Run_Time_Minutes'] = (crop_schedule['Water_Requirement_Greenhouse'] / motor_flow_rate) * 60

    full_schedule = pd.concat([full_schedule, crop_schedule], ignore_index=True)

    # Save the schedule to a CSV file
    full_schedule.to_csv(f'irrigation_schedule_{user_crop_name}.csv', index=False)
    print(f'\nIrrigation schedule for {user_crop_name} saved to irrigation_schedule_{user_crop_name}.csv')
else:
    print(f"Sorry, no data found for the crop {user_crop_name}.")
