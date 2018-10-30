from ast import literal_eval
import numpy as np

class Scanner:
    def scan_init(self, file_):

        logs = []
        counter = 0

        ranges_reading = False
        intensities_reading = False

        for line in file_:
            line = line.rstrip()
            if 'header:' in line:
                # if len(logs) > 0:
                    # logs[counter-1].ranges = logs[counter-1].ranges[7:].lstrip()
                    # logs[counter-1].ranges = np.array(literal_eval(logs[counter-1].ranges))
                    
                log = Scan()
                logs.append(log)
                counter = counter + 1          

            if 'seq:' in line:
                key,val = line.split(':')
                logs[counter-1].seq = int(val)

            elif 'secs:' in line:
                key,val = line.split(':')
                logs[counter-1].secs = int(val)

            elif 'nsecs:' in line:
                key,val = line.split(':')
                logs[counter-1].nsecs = int(val)

            elif 'frame_id:' in line:
                key,val = line.split(':')
                logs[counter-1].frame_id = val.lstrip()

            elif 'angle_min:' in line:
                key,val = line.split(':')
                logs[counter-1].angle_min = float(val)

            elif 'angle_max:' in line:
                key,val = line.split(':')
                logs[counter-1].angle_max = float(val)

            elif 'angle_increment:' in line:
                key,val = line.split(':')
                logs[counter-1].angle_increment = float(val)
            
            elif 'time_increment:' in line:
                key,val = line.split(':')
                logs[counter-1].time_increment = float(val)
            
            elif 'scan_time:' in line:
                key,val = line.split(':')
                logs[counter-1].scan_time = float(val)
            
            elif 'range_min:' in line:
                key,val = line.split(':')
                logs[counter-1].range_min = float(val)

            elif 'range_max:' in line:
                key,val = line.split(':')
                logs[counter-1].range_max = float(val)

            elif 'ranges:' in line:
                ranges_reading = True
                logs[counter-1].ranges = line

            elif 'intensities:' in line:
                ranges_reading = False
                intensities_reading = True

            elif ranges_reading:
                logs[counter-1].ranges = logs[counter-1].ranges + line

        return logs

class Scan:

    header = True
    
