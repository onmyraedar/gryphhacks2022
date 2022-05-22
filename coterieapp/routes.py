from coterieapp import app

@app.route("/")
@app.route("/home")
def home():
    return "<p>Homepage<p>"