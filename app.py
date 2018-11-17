import os
from os import path
import pathlib
from flask import Flask, flash, request, redirect, url_for
from flask import render_template
from werkzeug.utils import secure_filename
import numpy as np
from bokeh.plotting import *
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import ColumnDataSource, Slider, Range1d
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models.callbacks import CustomJS

import pandas as pd
from ast import literal_eval

from upload import allowed_file
from scan import Scan, Scanner

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

DF_GLOBAL = None
DF_ACT_GLOB = None
UPLOAD_FOLDER = '/uploads'

@app.route('/read', methods=['POST'])
def file_read():
    try:
        file_name = request.form.get("file_name")
    except ValueError as err:
        return "error %s" % err.args

    f = open(file_name, 'r')
    logdata = Scanner()
    logdata = logdata.scan_init(f)
    f.close()
    
    slide_values = []
    mini_slide_valx = []
    mini_slide_valy = []
    df_datas = []
    df_xdata = pd.DataFrame()
    df_ydata = pd.DataFrame()

    count = 1
    for log in logdata:
        key,val = log.ranges.split(':')
        log.ranges = val.lstrip()
        log.ranges = np.array(literal_eval(log.ranges))
        
        slide_values.append(log.seq)

        rad_space = np.linspace(log.angle_min, log.angle_max, len(log.ranges))
        df_data = pd.DataFrame()
        df_data['rad_space'] = rad_space
        df_data['range'] = log.ranges
        df_data['x'] = df_data['range'] * np.cos(df_data['rad_space'])
        df_data['y'] = df_data['range'] * np.sin(df_data['rad_space'])

        if count == 1:
            df_datas.append(df_data)

        count += 1
        if True:
            mini_slide_valx.append('x' + str(log.seq))
            mini_slide_valy.append('y' + str(log.seq))

            if df_xdata.empty:
                df_xdata = pd.DataFrame(df_data['x'])
                df_xdata.columns = mini_slide_valx
            else:
                df_x = pd.DataFrame(df_data['x'])
                df_xdata = pd.concat([df_xdata, df_x], ignore_index=True, axis=1)
                df_xdata.columns = mini_slide_valx

            if df_ydata.empty:
                df_ydata = pd.DataFrame(df_data['y'])
                df_ydata.columns = mini_slide_valy
            else:
                df_y = pd.DataFrame(df_data['y'])
                df_ydata = pd.concat([df_ydata, df_y], ignore_index=True, axis=1)
                df_ydata.columns = mini_slide_valy

    # charting
    data_len = len(df_datas[0].index)
    
    x_0 = [0] * data_len
    x_0[1] = df_datas[0]['x'][0]
    x_0[data_len-1] = df_datas[0]['x'][data_len-2]

    y_0 = [0] * data_len
    y_0[1] = df_datas[0]['y'][0]
    y_0[data_len-1] = df_datas[0]['y'][data_len-2]

    color_actual = '#0000AA'
    color_act = '#003300'
    DF_ACT_GLOB = pd.DataFrame({
        'x': df_datas[0]['x'].tolist(),
        'y': df_datas[0]['y'].tolist(),
        'x_0': x_0,
        'y_0': y_0
    })

    for colu in df_xdata:
        DF_ACT_GLOB[df_xdata[colu].name] = df_xdata[colu]
    for colu in df_ydata:
        DF_ACT_GLOB[df_ydata[colu].name] = df_ydata[colu]

    source = ColumnDataSource(DF_ACT_GLOB)

    fig = figure(title='lidar', plot_width=650, plot_height=650)
    
    left, right, bottom, top = -10, 10, -10, 10
    fig.x_range=Range1d(left, right)
    fig.y_range=Range1d(bottom, top)
    
    fig.line(source=source, x='x', y='y', 
            color=color_actual, line_width=2,
            alpha=0.8)
    fig.line(source=source, x='x_0', y='y_0', 
            color=color_act, line_width=2,
            alpha=0.7)

    callback = CustomJS(args=dict(source=source), code="""
        var f = cb_obj.value;
        var f_x = ('x' + f);
        var f_y = ('y' + f);

        var data = source.data;
        var x = data['x'];
        var y = data['y'];
        for (i = 0; i < x.length; i++) {
            x[i] = data[f_x][i];
            y[i] = data[f_y][i];
        }

        var x_0 = data['x_0'];
        var y_0 = data['y_0'];
        x_0[1] = x[1];
        y_0[1] = y[1];
        x_0[x.length-1] = x[x.length-2];
        y_0[y.length-1] = y[y.length-2];
        
        source.change.emit();
    """)

    if len(logdata) > 1:
        slider = Slider(start=min(slide_values), end=max(slide_values), step=1, value=min(slide_values), title='Lidar seq')
        slider.js_on_change('value', callback)
        layout = column(slider, fig)
        resources = INLINE.render()
        var = 6
        script, div = components(layout)
        html = render_template('embed.html', plot_script=script, plot_div=div, resources=resources, var=var)
    else:
        resources = INLINE.render()
        script, div = components(fig)
        html = render_template('embed.html', plot_script=script, plot_div=div, resources=resources)

    return html

@app.route('/list', methods=['GET'])
def file_list():
    cwd = os.getcwd()
    file_list = []
    for f in os.listdir(cwd):
        if f.endswith(".txt"):
            file_list.append(f)

    return render_template('list.html', files=file_list)

@app.route('/upload', methods=['GET', 'POST'])
def upload_log():
    return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        
        message = None
        
        file = None
        try:
            file = request.files['file']
            if file:
                # path = pathlib.Path.cwd()
                # path = pathlib.Path(UPLOAD_FOLDER)
                # path = path.joinpath(file.filename)
                # print(path)
                # path_ = pathlib.PurePath(UPLOAD_FOLDER)
                # path_ = path_.joinpath(file.filename)
                # print(f'{path_}')
                
                path = '/uploads/' + file.filename
                print(path)
                file.save(secure_filename(path))
                message = 'file can be saved.'

                # print("directory exists:" + str(path.exists(UPLOAD_FOLDER)))
                # dir_path = pathlib.Path(UPLOAD_FOLDER)
                # file_to_open = dir_path / file.filename
                # print(file_to_open)
                # print("is directory:" + str(file_to_open.is_dir()))
                
                # filename = secure_filename(filename)
                # filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                # filepath = pathlib.Path(filepath)
                # filepath = pathlib.Path(file.filename)
                # print(filepath)
                
                # file.save(secure_filename(file_to_open))
                
                # file.save(file_to_open)

                # if filepath.exists():
                #     message = 'file is already exist.'
                # else:
                #     message = 'file can be saved.'
                #     # file.save(filepath)
                #     message += '\nfile is saved...'
        except:
            message = 'cannot upload your file.'

    return message

@app.route('/')
def hello():
    return render_template('default.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
