from csv import excel
from msilib.schema import Error
import string
from flask import Blueprint, jsonify, request, make_response,render_template
import json
from enum import Enum
import requests
from sqlalchemy import Integer, exists
from .models import Movie
from . import db
import pdfkit

main = Blueprint('main', __name__)

# environemnt variables
api_key = '36a0c458'
req_url = 'http://www.omdbapi.com/'


INVALID_PARAMS = "Invalid params"
DATA_NOT_FOUND = "No data found"


class ErrorCodes(Enum):
    MISSING_PARAMS = {"code": 16000, "msg": "Missing params"}
    INVALID_PARAMS = {"code": 16001, "msg": "Invalid params"}
    DATA_NOT_FOUND = {"code": 16003, "msg": "No data found"}


class ValidParam(Enum):
    VALID_REQUEST = {"code": 200, "msg":"Done"}


@main.route('/movies_pdf/<offset>/<limit>')
def pdf(offset, limit):
    db_session = None
    db_session = db.session
    
    if not offset or not limit:
        return_val =  ErrorCodes.MISSING_PARAMS.value
        return return_val
    if not offset.isdigit() or not limit.isdigit():
        return_val = ErrorCodes.INVALID_PARAMS.value
        return return_val
    
    db_session = db.session
    movie_list = db_session.query(Movie)
    movie_list = movie_list.limit(int(limit))
    movie_list = movie_list.offset(int(offset) * int(limit)).all()
    rendered = render_template('./index.html', movies=movie_list)
    pdf = pdfkit.from_string(rendered)
    
    response =  make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=movies.pdf'
    return response

@main.route('/add_movie', methods = ['POST'])
def add_movie():
    try:
        db_session = None
        return_val = ValidParam.VALID_REQUEST.value
        movie_name = request.args.get('movie_name')
        if not movie_name:
            return_val =  ErrorCodes.MISSING_PARAMS.value
        
        db_session = db.session
        for movie in movie_name.split(","):
            movie = movie.strip()
            req_param = {"t": movie, "apikey": api_key}
            filter_criteria = db_session.query(exists().where(Movie.title == movie)).scalar()
            print(filter_criteria)

            if not filter_criteria:
                # movie =db_session.query(Movie).filter(Movie.title == movie).all()
                # if len(movie) == 0:
                resp = requests.get(req_url, params=req_param, verify=True)
                return_dict = (json.loads(resp.text))
                new_movie = Movie(title = movie, director =return_dict.get("Director"))
                db_session.add(new_movie)


        db_session.commit()
    except Exception as e:
        return_val = str(e), 400
    finally:
        if db_session:
            db_session.close()
        return return_val

@main.route('/movies', methods= ['GET'])
def movies():
    try:
        db_session = None
        return_val = None
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        
        if not offset or not limit:
            return_val =  ErrorCodes.MISSING_PARAMS.value
            return return_val
        if not offset.isdigit() or not limit.isdigit():
            return_val = ErrorCodes.INVALID_PARAMS.value
            return return_val
        
        db_session = db.session
        movie_list = db_session.query(Movie)
        movie_list = movie_list.limit(int(limit))
        movie_list = movie_list.offset(int(offset) * int(limit)).all()
        movies = []
        for movie in movie_list:
            movies.append({'title' : movie.title, 'director': movie.director})

        return_val = jsonify({'movies':movies})
    except Exception as e:
        return_val = str(e), 400
    finally:
        if db_session:
            db_session.close()
        return return_val


