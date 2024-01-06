from flask import Flask, render_template, request, send_file
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load the dataset of 100 crops
data = pd.read_csv('path_to_your_dataset.csv')  # Replace with the path to your dataset

def get_lifespan(crop_name, dataset):
    crop_data = dataset[dataset['Crop'] == crop_name]
    return crop_data['Life_Span (days)'].values[0] if not crop_data.empty else None

def generate_irrigation_schedule(user_crop_name):
    user_crop_lifespan = get_lifespan(user_crop_name, data)

    if user_crop_lifespan is not None:
        day_range = np.array(range(1, user_crop_lifespan + 1), dtype=float)

        water_requirement_per_day = data[data['Crop'] == user_crop_name]['Water_Requirement (mm)'].values
        water_requirement_per_day_crop = water_requirement_per_day * (1 + day_range / float(user_crop_lifespan))

        crop_schedule = pd.DataFrame({
            'Crop': [user_crop_name] * user_crop_lifespan,
            'Day': day_range,
            'Water_Requirement_Crop': water_requirement_per_day_crop,
            'Water_Requirement_Greenhouse': water_requirement_per_day_crop * 0.001 * 17 * 14
        })

        motor_flow_rate = 1.0
        crop_schedule['Motor_Run_Time_Minutes'] = (crop_schedule['Water_Requirement_Greenhouse'] / motor_flow_rate) * 60

        return crop_schedule
    else:
        return pd.DataFrame()

@app.route('/')
def index():
    crop_list = data['Crop'].tolist()
    return render_template('index.html', crop_list=crop_list)

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    user_crop_name = request.form['crop_name']
    schedule = generate_irrigation_schedule(user_crop_name)

    if not schedule.empty:
        file_path = f'irrigation_schedule_{user_crop_name}.csv'
        schedule.to_csv(file_path, index=False)
        return render_template('result.html', schedule=schedule, file_path=file_path)
    else:
        return render_template('result.html', schedule=None, file_path=None)

@app.route('/download/<file_path>')
def download(file_path):
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
