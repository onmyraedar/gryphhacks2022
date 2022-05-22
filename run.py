import os
from coterieapp import app

if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    app.run('localhost', 8080, debug=True)