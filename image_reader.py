import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
from flask import render_template
import datetime
import time
try:
    import Image
except:
    from PIL import Image
import pytesseract
import urllib

HOME = '/home/ubuntu/temp/python/image_reader'
UPLOAD_FOLDER = HOME + '/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'JPG','PNG','jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
import logging
logging.basicConfig(filename=HOME + '/logging.log',level=logging.DEBUG)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploadform', methods=['GET'])
def my_form():
    return render_template("form.html")

@app.route('/upload', methods=['POST'])
def upload_url_form_post():
    print os.path.abspath(__file__)
    try:
        text = request.form['text']
        processed_text = text
        print processed_text
        ts = time.time()
        filename = HOME + "/input/trailhead-" +  datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S') + ".png"

        urllib.urlretrieve(processed_text,filename)
        t = processImage(filename)
        try:
            os.remove(filename)
        except Exception as x:
            logging.error(x)
            logging.error( "unable to remove file:" + filename)
    except Exception as e:
        logging.error(e)
        return str(e)
    return t

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                ts = time.time()
                filename = filename +  datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filePath = UPLOAD_FOLDER + '/' + filename
                t = processImage(filePath)
                try:
                    os.remove(filePath)
                except Exception as x:
                    logging.error(x)
                    logging.error( "unable to remove file:" + filename)
                return t

            except Exception as e:
                logging.error(e)
                return "Error:" + e
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
def processImage(filepath):
    text = pytesseract.image_to_string(Image.open(filepath))
    logging.debug(text)
    textArray = text.split("\n")
    badge_count = 0
    i = 0
    prev_line = ''
    for line in textArray:
        line = line.lstrip(' ').rstrip(' ')
        print line
        if line != '':
            l_length = line.__sizeof__()
            #if prev_line.startswith('Home') & prev_line.split(' ').__sizeof__() < 5:
            #    print ">>>" + line
            #    return 'Error:' + prev_line + ' ' + line
            if line.startswith('Home Trails Modules Projects') & line.endswith('Points') or line.startswith('Home Trails') :
                lineA = line.split(' ')
                if lineA.__sizeof__() > 5:
                    temp = lineA[7]
                    e5 = lineA[5]
                    e6 = lineA[6]
                    if (temp == '-') & (lineA[9] == 'Badges'):
                        temp = lineA[8]
                    elif temp.__eq__('-') & e5.__eq__('-') :
                        if e6.__eq__('zaadges') | e6.startswith('z'):
                            temp = str(2)
                    if temp.startswith("s"):
                        temp = "5" + temp[1:]
                    logging.debug("badge_count: " + temp)
                    if temp.__eq__('-'):
                        e5 = lineA[5]
                        e6 = lineA[6]

                    return temp

            elif line.startswith('Home Tvails') :
                lineA = line.split(' ')
                if lineA.__len__() > 5:
                    e6 = lineA[6]
                    e7 = lineA[7]
                    badge_count = ''
                    if e7.__eq__('was'):
                        if e6.isdigit():
                            badge_count = e6
                        elif e6.__eq__('a'):
                            badge_count = str(0)
                    elif e6.__eq__('a'):
                        badge_count = str(0)

                    return badge_count
            elif line[0:1].isdigit():
                lineA = line.split(' ')
                lineA_len = lineA.__len__()
                last_char = lineA[lineA_len -1]
                if last_char.isdigit():
                    if not textArray[i+1].lower().startswith("in progress"):
                        badge_count = lineA[lineA_len -2]
                        logging.debug("badge_count:" + badge_count)
                        return badge_count
                    elif textArray[i+1].lower().startswith("tra"):
                        badge_count = lineA[lineA_len -2]
                        logging.debug("badge_count: " + badge_count)
                        badge_count

                elif last_char == '-':
                    badge_count = lineA[lineA_len - 3]
                    return badge_count
                elif line.endswith('Trailhead Points'):
                    lineA = line.split(' ')
                    lineA_len = lineA.__len__()
                    badge_count = lineA[1][1:]
                    logging.debug("badge_count: " + badge_count)
                    return badge_count

        prev_line = line
        i += 1
    logging.debug("came here returning error")
    return "Error: " + text



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = False)
