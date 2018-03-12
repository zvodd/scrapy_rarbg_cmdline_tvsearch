import base64
import tempfile
import webbrowser
import argparse
import time

REPLACE_EGG = "#@^REPLACEEGG^#@"
TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Preview Html</title>
    <link rel="stylesheet" href="">
    <style type="text/css" media="screen">
        .html-preview-frame {
            box-sizing: border-box;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.5);
            margin: 0;
            width: 100%;
            height: calc(100vh - 20px);
        }    
    </style>

    <script>
      function createPreviewFrame() {
        var dataURL = `#@^REPLACEEGG^#@`;
        const iframe = document.createElement('iframe');
        iframe.className = 'html-preview-frame';
        iframe.setAttribute('sandbox', '');  // Forbid to run JavaScript and set unique origin.
        iframe.setAttribute('src', dataURL);
        document.body.appendChild(iframe);
      }
      document.onreadystatechange = function readyStateChanged() {
        if (document.readyState === "interactive") {
          createPreviewFrame();
        }
      };
    </script>
</head>
<body>
    
</body>
</html>
"""


def create_data_uri(raw_string, mime_type="text/html"):
    urischeme = "data:{};base64,".format(mime_type)
    bc = base64.b64encode(raw_string.encode('latin-1'))
    return "{}{}".format(urischeme, bc.decode('latin-1'))


def make_preview(htmlstring, wait_time=0):
    with tempfile.NamedTemporaryFile(mode='w', delete=True) as tf:
        src = TEMPLATE.replace(REPLACE_EGG, create_data_uri(htmlstring))
        tf.write(src)

        # for some reason in python2 (windows) the tempfile here output is limited at 24,598 bytes
        # with open("wtf_log.log", 'w') as wtfh:
        #     wtfh.write(src)

        time.sleep(0.2)
        url = "file://{}".format(tf.name)
        webbrowser.open(url, new=1, autoraise=True)

        # wait a sec for the browser to open the file before removing
        if wait_time is not 0:
            time.sleep(wait_time)
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('html_file', help='html src file, to be rendering in sandboxed iframe')
    parser.add_argument('-w', '--wait',
                        help='time to wait for browser to open, before deleting tempfile.'
                        'Default is 5 seconds',
                        type=int, default=5)
    args = parser.parse_args()

    with open(args.html_file, 'rb') as fh:
        html = fh.read().decode('latin-1')
        make_preview(html, args.wait)
    return


if __name__ == '__main__':
    main()
