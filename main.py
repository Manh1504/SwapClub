from flask import Flask, render_template, request, redirect, url_for, session

app:Flask = Flask (__name__)
@app.route('/')
def index():
    return ("welcome")
if __name__ == '__main__':
    app.run(debug=True, port=8080)


