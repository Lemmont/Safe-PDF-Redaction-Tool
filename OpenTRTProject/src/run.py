from flask import Flask, jsonify, render_template, request
import argparse

from OpenTRT import RedactFile

app = Flask(__name__)


def main():

    # Get arguments
    parser = argparse.ArgumentParser(description="Redact a PDF file")
    parser.add_argument('file', help="PDF file to be redacted")
    parser.add_argument('-n', '--num', help="number of (randomly) selected charachter sequences to redact", default=0, type=int)
    parser.add_argument('--input', nargs='+', type=str, help="charachter sequences to redact", default=[])
    parser.add_argument('mode', choices=['replace', "white"], help="Either add a replacement value [x] ('replace') or do not replace redacted values ('white')")
    parser.add_argument('-m', '--metadata',help="Search (xml) metadata for to-be-redacted values.", action='store_true')
    parser.add_argument('-s', '--save_steps', help="Save intermediate steps in PDF documents.", action='store_true')
    args = parser.parse_args()


    file = args.file
    input = args.input
    metadata = args.metadata
    num = args.num
    save_step = args.save_steps
    mode = args.mode

    """
        Local website
    """
    # @app.route('/')
    # @app.route('/<file>')
    # def home(file=file):
    #     return render_template('index.html', file=file, run_status="False")


    # @app.route('/run_function', methods=['POST'])
    # def run_function():
    #     redact_file(file, num=num, mode=mode, input=input, save_steps=save_step)
    #     return render_template('index.html', message="Function executed!", run_status = 'completed')

    # @app.route('/', methods=['POST'])
    # def upload_file():
    #     if 'file' not in request.files:
    #         return jsonify(error='No file part')

    #     file = request.files['file']

    #     if file.filename == '':
    #         return jsonify(error='No selected file')

    #     # Process the file (you can save it to the server, perform further actions, etc.)
    #     # In this example, we just print the file name
    #     print('Uploaded file:', file.filename)

    #     return jsonify(success=file.filename)


    # app.run(debug=True)

    print(num)

    RedactFile.redact_file(file, num=num, mode=mode, input=input, save_steps=save_step)


# Using the special variable
# __name__
if __name__=="__main__":
    main()