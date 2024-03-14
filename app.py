import numpy as np
import pandas as pd
import seaborn as sns
from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.sensors import IMU, Electrics, Damage
from google.cloud import bigquery


def game(player_id):
    beamng = BeamNGpy('localhost', 64256, home='D:/SteamLibrary/steamapps/common/BeamNG.drive', user='D:/miracle/code/game/user')
    beamng.open()

    scenario = Scenario('automation_test_track', 'Driving Analysis - Miracle Software Systems')

    vehicle = Vehicle('test_vehicle', model='covet', license = player_id, color='Green')
    imu_sensor = IMU(pos=(0.73, 0.51, 0.8), debug=True)
    electrics_sensor = Electrics()
    damage_sensor = Damage()

    vehicle.sensors.attach('imu_sensor', imu_sensor)
    vehicle.sensors.attach('electrics_sensor', electrics_sensor)
    vehicle.sensors.attach('damage_sensor', damage_sensor)

    scenario.add_vehicle(vehicle, pos=(497.1917725, 178.2896118, 131.7432404), rot_quat=(0.002234787144, -0.0014619524, 0.6965841062, 0.7174701746))
    scenario.make(beamng)
    data = []
    column_names = ['Time'] 


    essential_keys = [
        'speed', 'accXSmooth', 'accYSmooth', 'accZSmooth', 'gear', 'rpm', 'brake', 'throttle',
        'fuel', 'oil_temperature', 'water_temperature', 'steering', 'wheelspeed', 'part_damage', 'horn'
    ]

    beamng.scenario.load(scenario)
    beamng.settings.set_deterministic()
    beamng.settings.set_steps_per_second(60)
    beamng.scenario.start()
    beamng.control.pause()

    vehicle.switch()
    beamng.control.step(240)

    for t in range(0, 1800, 30):
        vehicle.sensors.poll()
        
    
        row_data = {'Time': t/60}
        
   
        for sensor_name, sensor in vehicle.sensors.items():
            filtered_data = {key: value for key, value in sensor.data.items() if key in essential_keys}
            row_data.update({f"{key}": value for key, value in filtered_data.items()})
        
    
        if t == 0:
            column_names.extend(sorted(row_data.keys())[1:])  # Exclude 'Time' since it's already added
        

        data.append([row_data[col] for col in column_names])
        beamng.control.step(30)

    beamng.close()


    df = pd.DataFrame(data, columns=column_names)

 
    df.to_csv(f'telematics/{player_id}_vehicle_data.csv', index=False)
    
    upload_to_bigquery(f'telematics/{player_id}_vehicle_data.csv', player_id)
    


    print(df.head())

def upload_to_bigquery(csv_file_path, table_id):
    client = bigquery.Client()
    table_id_full = f"fresh-span-400217.simulated_vehicle_data.{table_id}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  
        autodetect=True, 
    )

    with open(csv_file_path, "rb") as source_file:
        load_job = client.load_table_from_file(source_file, table_id_full, job_config=job_config)

    load_job.result()  

    destination_table = client.get_table(table_id_full)
    print(f"Loaded {destination_table.num_rows} rows into {table_id_full}.")
    
