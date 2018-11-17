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
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, Band, Slider
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
    df_datas = []
    df_xdata = []
    df_ydata = []

    count = 0
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
        count = count + 1
        if count < 10 and count > 3:
            df_xdata = df_xdata + df_data['x'].tolist()
            df_ydata = df_ydata + df_data['y'].tolist()
            count = count + 1

        df_datas.append(df_data)

    # charting
    color_actual = '#0000AA'
    DF_ACT_GLOB = pd.DataFrame({
        'x': df_datas[0]['x'].tolist(),
        'y': df_datas[0]['y'].tolist()
    })
    source = ColumnDataSource(DF_ACT_GLOB)

    # DF_ACT_GLOB = pd.DataFrame({
    #     'x': df_xdata,
    #     'y': df_ydata
    # })
    GLOB = pd.DataFrame({
        'x': df_xdata,
        'y': df_ydata
    })
    Curr = ColumnDataSource(GLOB)
    
    print('process')

    fig = figure(title='lidar', plot_width=800, plot_height=800)
    fig.line(source=source, x='x', y='y', 
            color=color_actual, line_width=2,
            alpha=0.8)

    fig.vbar(x='x', top='x', width=0.2, color='#ffffff', alpha=0.0, source=Curr)

    color_act = '#009900'
    for index, row in DF_ACT_GLOB.iterrows():
        df_act = pd.DataFrame({
            'x': [0, row['x']],
            'y': [0, row['y']]
        })
        ds_act = ColumnDataSource(df_act)
        fig.line(source=ds_act, x='x', y='y', 
            color=color_act, line_width=2,
            alpha=0.8)

    callback = CustomJS(args=dict(source=source, sc=Curr), code="""
        var data = source.data;
        var data_all = Curr.data;

        var f = cb_obj.value
        var x = data['x']
        var y = data['y']
        var len_data = x.length
        var cursor = f * len_data
        for (var i = 0; i < len_data; i++) {
            x = data_all['x']
            y = data_all['y']
        }
        source.change.emit();
    """)
    
    if len(logdata) > 1:
        slider = Slider(start=min(slide_values), end=max(slide_values), step=1, value=min(slide_values), title='Lidar seq')
        # slider = Slider(start=0, end=max(slide_values)-min(slide_values), step=1, value=0, title='Lidar seq')
        # slider = Slider(start=1, end=5, step=1, value=1, title='Lidar seq')
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

# def printing():
#     print('asdf')
#     return 'asdf'
# def update_data(attr, old, new):
#     # n = slide.value
#     DF_ACT_GLOB.data = DF_GLOBAL[10]

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
