import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
import datetime
import time
try:
    import Image
except:
    from PIL import Image
import pytesseract

UPLOAD_FOLDER = '/home/ubuntu/temp/python/image_reader/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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
                text = pytesseract.image_to_string(Image.open(UPLOAD_FOLDER + '/' + filename))
                print text
                textArray = text.split("\n")
                badge_count = 0
                i = 0
                for line in textArray:
                    line = line.lstrip(' ').rstrip(' ')
                    print line
                    if line != '':
                        l_length = line.__sizeof__()

                        if line[0:1].isdigit():
                            lineA = line.split(' ')
                            lineA_len = lineA.__len__()
                            last_char = lineA[lineA_len -1]
                            if last_char.isdigit():
                                if not textArray[i+1].lower().startswith("in progress"):
                                    badge_count = lineA[lineA_len -2]
                                    print "badge_count>>" + badge_count
                                    return badge_count
                                elif textArray[i+1].lower().startswith("tra"):
                                    badge_count = lineA[lineA_len -2]
                                    print "badge_count>>" + badge_count
                                    return badge_count

                            elif last_char == '-':
                                badge_count = lineA[lineA_len - 3]
                                return badge_count
                            elif line.endswith('Trailhead Points'):
                                lineA = line.split(' ')
                                lineA_len = lineA.__len__()
                                return lineA[1][1:]

                        elif line.startswith('Home Trails Modules Projects') & line.endswith('Points'):
                            lineA = line.split(' ')
                            return lineA[7]
                    i += 1
                return "Error: " + text
                        #print line

                # if text.startswith("tra"):
                #     b = text.index("Badges")
                #     print b
                #     b1 = text[b - 2: b -1]
                #     b2 = text[b - 4: b - 3]
                #
                #     if b2.isdigit() & b1.isdigit():
                #         badge_count = b2 + b1
                #     elif b1.lstrip(" ").rstrip(" ").isdigit():
                #         badge_count = b1
                #     else:
                #         return "error processing:" + text
                # else:
                #     if text[0:1].isdigit():
                #         b1 = text.index("t")
                #         try:
                #             b2 = text.index(" ")
                #         except Exception as e:
                #             b2 = text.index(".")
                #
                #         badge_count = text[b2 :b1]
                #         if badge_count.startswith("."):
                #             badge_count = badge_count[1:]
                #         if badge_count.startswith(" ."):
                #             badge_count = badge_count[2:]
                #     else:
                #         return "error processing:" + text
                # print badge_count
                # return "badge_count:" + badge_count
            except Exception as e:
                print e
            #return file.filename
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = False)
