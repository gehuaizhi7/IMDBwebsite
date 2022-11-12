#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from datetime import date


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "eh2974"
DB_PASSWORD = "w4111"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  # print (request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM movie")
  names = []
  for result in cursor:
    names.append((result['movie_id'],result['title']))  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#

@app.route('/movie/<movieid>')
def get_movie(movieid):
  cmd = 'SELECT * FROM movie WHERE movie_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = movieid)
  movie = []
  for i in cursor:
    movie.append(i)
  cursor.close()

  cmd = 'SELECT * FROM produce JOIN production_company ON produce.company_id=production_company.company_id WHERE movie_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = movieid)
  company = []
  for i in cursor:
    company.append(i)
  cursor.close()

  cmd = 'SELECT * FROM genre JOIN ispartof ON genre.genre_id=ispartof.genre_id WHERE movie_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = movieid)
  genre = []
  for i in cursor:
    genre.append(i)
  cursor.close()

  cmd = 'SELECT * FROM personnel JOIN direct ON personnel.person_id=direct.person_id WHERE movie_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = movieid)
  director = []
  for i in cursor:
    director.append(i)
  cursor.close()

  cmd = 'SELECT * FROM personnel JOIN actor ON personnel.person_id=actor.person_id JOIN role ON personnel.person_id=role.person_id WHERE movie_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = movieid)
  actor = []
  for i in cursor:
    actor.append(i)
  cursor.close()

  cmd = 'SELECT * FROM feedback WHERE movie_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = movieid)
  feedback = []
  for i in cursor:
    feedback.append(i)
  cursor.close()

  context = dict(movie = movie[0], feedback = feedback, company = company[0], genre = genre[0], director = director[0], actor = actor)
  return render_template("moviedetails.html", **context)

# @app.route('/newmovie')
# def another():
#   return render_template("newmovie.html")


# Example of adding new data to the database
@app.route('/movie/<movieid>/addfeedback', methods=['POST'])
def addfeedback(movieid):
  cmd = 'SELECT COUNT(*) FROM feedback'
  cursor = g.conn.execute(text(cmd))
  count = []
  for i in cursor:
    count.append(i)
  cursor.close()
  count = count[0][0]

  cmd = 'SELECT COUNT(*) FROM userimdb'
  cursor = g.conn.execute(text(cmd))
  usercount = []
  for i in cursor:
    usercount.append(i)
  cursor.close()
  usercount = usercount[0][0]

  content = request.form['feedback']
  userid = request.form['uid']
  rating = request.form['rating']
  password = request.form['password']
  if not userid.isnumeric() or not rating.isnumeric(): return redirect('/error')
  if int(userid)<=0 or int(userid)>usercount: return redirect('/error')
  if int(rating)<0 or int(rating)>10: return redirect('/error')

  cmd = 'SELECT * FROM userimdb WHERE uid=(:id)'
  cursor = g.conn.execute(text(cmd),id = userid)
  user = []
  for i in cursor:
    user.append(i)
  cursor.close()

  if user[0][2]!=password: return redirect('/error')

  cmd = 'INSERT INTO feedback VALUES ((:feedbackid),(:movieid),(:uid),(:content),(:rating),(:date))'
  g.conn.execute(text(cmd), feedbackid = count+1, movieid = movieid, uid = userid, content = content, rating = rating, date = date.today())
  return redirect('/movie/'+movieid)


@app.route('/feedback/<feedbackid>')
def get_feedback(feedbackid):
  cmd = 'SELECT * FROM feedback WHERE feedback_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = feedbackid)
  feedback = []
  for i in cursor:
    feedback.append(i)
  cursor.close()

  cmd = 'SELECT * FROM comment WHERE feedback_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = feedbackid)
  comment = []
  for i in cursor:
    comment.append(i)
  cursor.close()

  context = dict(feedback = feedback[0], comment = comment)
  return render_template("feedbackdetails.html", **context)

@app.route('/feedback/<feedbackid>/addcomment', methods=['POST'])
def addcomment(feedbackid):
  cmd = 'SELECT COUNT(*) FROM comment'
  cursor = g.conn.execute(text(cmd))
  count = []
  for i in cursor:
    count.append(i)
  cursor.close()
  count = count[0][0]

  cmd = 'SELECT COUNT(*) FROM userimdb'
  cursor = g.conn.execute(text(cmd))
  usercount = []
  for i in cursor:
    usercount.append(i)
  cursor.close()
  usercount = usercount[0][0]

  content = request.form['comment']
  userid = request.form['uid']
  password = request.form['password']
  if not userid.isnumeric(): return redirect('/error')
  if int(userid)<=0 or int(userid)>usercount: return redirect('/error')

  cmd = 'SELECT * FROM userimdb WHERE uid=(:id)'
  cursor = g.conn.execute(text(cmd),id = userid)
  user = []
  for i in cursor:
    user.append(i)
  cursor.close()

  if user[0][2]!=password: return redirect('/error')

  cmd = 'INSERT INTO comment VALUES ((:commentid),(:feedbackid),(:uid),(:content),(:date))'
  g.conn.execute(text(cmd), commentid = count+1, feedbackid = feedbackid, uid = userid, content = content, date = date.today())
  return redirect('/feedback/'+feedbackid)

@app.route('/user/<uid>')
def get_user(uid):
  cmd = 'SELECT * FROM userimdb WHERE uid=(:id)'
  cursor = g.conn.execute(text(cmd),id = uid)
  userimdb = []
  for i in cursor:
    userimdb.append(i)
  cursor.close()

  context = dict(user = userimdb[0])
  return render_template("userdetails.html", **context)

@app.route('/company/<companyid>')
def get_company(companyid):
  cmd = 'SELECT * FROM production_company WHERE company_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = companyid)
  company = []
  for i in cursor:
    company.append(i)
  cursor.close()

  context = dict(company = company[0])
  return render_template("companydetails.html", **context)

@app.route('/genre/<genreid>')
def get_genre(genreid):
  cmd = 'SELECT * FROM genre WHERE genre_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = genreid)
  genre = []
  for i in cursor:
    genre.append(i)
  cursor.close()

  context = dict(genre = genre[0])
  return render_template("genredetails.html", **context)

@app.route('/person/<personid>')
def get_person(personid):
  cmd = 'SELECT * FROM personnel WHERE person_id=(:id)'
  cursor = g.conn.execute(text(cmd),id = personid)
  person = []
  for i in cursor:
    person.append(i)
  cursor.close()

  context = dict(person = person[0])
  return render_template("persondetails.html", **context)

@app.route('/register')
def register():
  cmd = 'SELECT COUNT(*) FROM userimdb'
  cursor = g.conn.execute(text(cmd))
  count = []
  for i in cursor:
    count.append(i)
  cursor.close()
  count = count[0][0]
  
  context = dict(uid = count+1)
  return render_template("register.html", **context)


@app.route('/register', methods=['POST'])
def register_post():
  cmd = 'SELECT COUNT(*) FROM userimdb'
  cursor = g.conn.execute(text(cmd))
  count = []
  for i in cursor:
    count.append(i)
  cursor.close()
  count = count[0][0]

  username = request.form['username']
  password = request.form['password']
  cmd = 'INSERT INTO userimdb VALUES ((:uid),(:username),(:password))'
  g.conn.execute(text(cmd), uid = count+1, username = username, password = password)
  return redirect('/')

@app.route('/error')
def error():
  return render_template("error.html")

# @app.route('/newmovie')
# def another():
#   return render_template("newmovie.html")

# @app.route('/login')
# def login():
#     abort(401)
#     this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()