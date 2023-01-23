# from recommend_models import get_top_k_collaborators_by_author, get_top_k_papers_by_author

import json

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import func, desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://aminer:team13best@aminer_postgres_db/aminer_db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route('/')
def home():
    return 'Hello, Aminer!'


db = SQLAlchemy(app)
ma = Marshmallow(app)


# "authors" table declaration
class Authors(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    org = db.Column(db.String(4000))

    def __init__(self, name=None, org=None):
        self.name = name
        self.org = org


class AuthorSchema(ma.Schema):
    class Meta:
        fields = ("name", "org")

    def get_fields(self):
        return self.Meta.fields


author_schema = AuthorSchema(many=False)
authors_schema = AuthorSchema(many=True)


# "author_paper" table declaration
class AuthorPapers(db.Model):
    __tablename__ = 'author_paper'

    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer)
    author_id = db.Column(db.Integer)

    def __init__(self, paper_id=None, author_id=None):
        self.paper_id = paper_id
        self.author_id = author_id


class AuthorPaperSchema(ma.Schema):
    class Meta:
        fields = ("paper_id", "author_id")

    def get_fields(self):
        return self.Meta.fields


author_paper_schema = AuthorPaperSchema(many=False)
author_papers_schema = AuthorPaperSchema(many=True)


# "venues" table declaration
class Venues(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    raw = db.Column(db.String(100))
    publisher = db.Column(db.String(500))
    issn = db.Column(db.String(500))
    isbn = db.Column(db.String(500))

    def __init__(self, raw=None, publisher=None, issn=None, isbn=None):
        self.raw = raw
        self.publisher = publisher
        self.issn = issn
        self.isbn = isbn


class VenueSchema(ma.Schema):
    class Meta:
        fields = ("raw", "publisher", "isin", "isbn")

    def get_fields(self):
        return self.Meta.fields


venue_schema = VenueSchema(many=False)
venues_schema = VenueSchema(many=True)


# "papers_refs" table declaration
class PaperReferences(db.Model):
    __tablename__ = 'papers_refs'

    id = db.Column(db.Integer, primary_key=True)
    parent_paper = db.Column(db.Integer)
    child_paper = db.Column(db.Integer)

    def __init__(self, parent_paper=None, child_paper=None):
        self.parent_paper = parent_paper
        self.child_paper = child_paper


class PaperReferenceSchema(ma.Schema):
    class Meta:
        fields = ("parent_paper", "child_paper")

    def get_fields(self):
        return self.Meta.fields


paper_reference_schema = PaperReferenceSchema(many=False)
paper_references_schema = PaperReferenceSchema(many=True)


# "paper_tags" table declaration
class PaperTags(db.Model):
    __tablename__ = 'papers_tags'

    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer)

    def __init__(self, paper_id=None, tag_id=None):
        self.paper_id = paper_id
        self.tag_id = tag_id


class PaperTagsSchema(ma.Schema):
    class Meta:
        fields = ("paper_id", "tag_id")

    def get_fields(self):
        return self.Meta.fields


paper_tag_schema = PaperTagsSchema(many=False)
paper_tags_schema = PaperTagsSchema(many=True)


# "tags" table declaration
class Tags(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(200))

    def __init__(self, tag_name=None):
        self.tag_name = tag_name


class TagSchema(ma.Schema):
    class Meta:
        fields = ("tag_name",)

    def get_fields(self):
        return self.Meta.fields


tag_schema = TagSchema(many=False)
tags_schema = TagSchema(many=True)


# "user" table declaration
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20))
    password = db.Column(db.String(20))

    def __init__(self, login=None, password=None):
        self.login = login
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ("login", "password")

    def get_fields(self):
        return self.Meta.fields


user_schema = UserSchema(many=False)
users_schema = UserSchema(many=True)


# "papers" table declaration
class Papers(db.Model):
    __tablename__ = 'papers'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer)
    title = db.Column(db.String(2000))
    abstract = db.Column(db.String(150000))
    year = db.Column(db.Integer)
    n_citation = db.Column(db.Integer)
    page_start = db.Column(db.String(100))
    page_end = db.Column(db.String(100))
    issue = db.Column(db.String(100))
    volume = db.Column(db.String(100))
    keywords = db.Column(db.String(7000))
    fos = db.Column(db.String(4000))
    doi = db.Column(db.String(700))
    pdf = db.Column(db.String(700))
    url = db.Column(db.String(15000))

    def __init__(self, venue_id=None, title=None, abstract=None,
                 year=None, n_citation=None, page_start=None,
                 page_end=None, issue=None, volume=None,
                 keywords=None, fos=None, doi=None, pdf=None,
                 url=None):
        self.venue_id = venue_id
        self.title = title
        self.abstract = abstract
        self.year = year
        self.n_citation = n_citation
        self.page_start = page_start
        self.page_end = page_end
        self.issue = issue
        self.volume = volume
        self.keywords = keywords
        self.fos = fos
        self.doi = doi
        self.pdf = pdf
        self.url = url


class PaperSchema(ma.Schema):
    class Meta:
        fields = ("venue_id", "title", "abstract", "year",
                  "n_citation", "page_start", "page_end",
                  "issue", "volume", "keywords", "fos", "doi",
                  "pdf", "url")

    def get_fields(self):
        return self.Meta.fields


paper_schema = PaperSchema(many=False)
papers_schema = PaperSchema(many=True)


# "papers" table methods
@app.route("/get_papers", methods=['GET'])
def get_papers():
    return jsonify(papers_schema.dump(Papers.query.all()))


@app.route("/get_paper/<int:id>", methods=['GET'])
def get_paper_by_id(id):
    return paper_schema.jsonify(Papers.query.get_or_404(int(id)))

@app.route("/get_paper_by_year/<int:year>", methods=['GET'])
def get_paper_by_year(year):
    return papers_schema.jsonify(Papers.query.filter_by(year=year).all())

@app.route("/get_paper_by_author_name/<string:author_name>", methods=['GET'])
def get_paper_by_author_name(author_name):
    author_id = Authors.query.filter_by(name=author_name).first().id
    author_paper_ids = AuthorPapers.query.filter_by(author_id=author_id).all()
    res_papers = []
    for author_paper_id in author_paper_ids:
        res_papers.append(Papers.query.get_or_404(author_paper_id.paper_id))
    return jsonify(papers_schema.dump(res_papers))

@app.route("/get_paper_by_vanue_raw/<string:vanue_raw>", methods=['GET'])
def get_paper_by_vanue_raw(vanue_raw):
    venues = Venues.query.filter_by(raw=vanue_raw).all()
    res_papers = []
    for venue in venues:
        papers = Papers.query.filter_by(venue_id=venue.id).all()
        for paper in papers:
            res_papers.append(paper)
    return jsonify(papers_schema.dump(res_papers))

@app.route("/get_papers_by_tag/<string:tag>", methods=['GET'])
def get_paper_by_tag(tag):
    tag_id = Tags.query.filter_by(tag_name=tag).first().id
    paper_ids = PaperTags.query.filter_by(tag_id=tag_id).all()
    paper_ids = [paper_id.paper_id for paper_id in paper_ids]
    return papers_schema.jsonify(
        Papers.query.filter(Papers.id.in_(paper_ids)).all()
    )

# @app.route("/recommmend_papers_by_author_name/<string:author_name>", methods=['GET'])
# def recommmend_papers_by_author_name(author_name):
#     author_id = Authors.query.filter_by(name=author_name).first().id
#     res = []
#     for id in get_top_k_papers_by_author(author_id):
#         res.append(Papers.query.get_or_404(int(id)))
#     return jsonify(papers_schema.dump(res))

@app.route("/add_paper", methods=['POST'])
def add_paper():
    request_data = request.get_json()
    venue_id = None
    title = None
    abstract = None,
    year = None
    n_citation = None
    page_start = None,
    page_end = None
    issue = None
    volume = None,
    keywords = None
    fos = None
    doi = None
    pdf = None,
    url = None
    if "venue_id" in request_data:
        venue_id = request_data["venue_id"]
    if "title" in request_data:
        title = request_data["title"]
    if "abstract" in request_data:
        abstract = request_data["abstract"]
    if "year" in request_data:
        year = int(request_data["year"])
    if "n_citation" in request_data:
        n_citation = int(request_data["n_citation"])
    if "page_start" in request_data:
        page_start = int(request_data["page_start"])
    if "page_end" in request_data:
        page_end = int(request_data["page_end"])
    if "issue" in request_data:
        issue = request_data["issue"]
    if "volume" in request_data:
        volume = request_data["volume"]
    if "keywords" in request_data:
        keywords = request_data["keywords"]
    if "fos" in request_data:
        fos = request_data["fos"]
    if "doi" in request_data:
        doi = request_data["doi"]
    if "pdf" in request_data:
        pdf = request_data["pdf"]
    if "url" in request_data:
        url = request_data["url"]
    entry = Papers(venue_id, title, abstract, year, n_citation,
                   page_start, page_end, issue, volume,
                   keywords, fos, doi, pdf, url)
    db.session.add(entry)
    db.session.commit()

    return "Ok"


@app.route("/delete_paper", methods=['POST'])
def delete_paper():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        Papers.query.filter(Papers.id == id).delete()
        db.session.commit()

    return "Ok"


@app.route("/update_paper", methods=['POST'])
def update_paper():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        papers = Papers.query.filter(Papers.id == id)
        paper_schema_fields = paper_schema.get_fields()
        for param_name, param_value in request_data.items():
            if (param_name != "id") and (param_name in paper_schema_fields):
                for paper in papers:
                    setattr(paper, param_name, param_value)

        db.session.commit()

    return "Ok"


# "authors" table methods
@app.route("/get_authors", methods=['GET'])
def get_authors():
    return jsonify(authors_schema.dump(Authors.query.all()))


@app.route("/get_author/<int:id>", methods=['GET'])
def get_author_by_id(id):
    return author_schema.jsonify(Authors.query.get_or_404(int(id)))


@app.route("/get_top_authors_by_tag/<string:tag>", methods=['GET'])
def get_top_authors_by_tag(tag):
    tag_id = Tags.query.filter_by(tag_name=tag).first().id
    paper_ids = PaperTags.query.filter_by(tag_id=tag_id).all()
    paper_ids = [paper_id.paper_id for paper_id in paper_ids]
    query_result = db.session.query(
        Authors.name.label("author_name"),
        func.sum(Papers.n_citation).label("author_citations")
    ).join(
        AuthorPapers, Authors.id == AuthorPapers.author_id
    ).join(
        Papers, AuthorPapers.paper_id == Papers.id
    ).filter(
        AuthorPapers.paper_id.in_(paper_ids)
    ).group_by(
        Authors.name
    ).order_by(
        func.sum(Papers.n_citation).desc()
    ).limit(10).all()

    query_result = [{"author_name" : res[0], "author_citations" : res[1]} for res in query_result]
    return query_result
    
# @app.route("/recommmend_collaborators_by_author_name/<string:author_name>", methods=['GET'])
# def recommmend_collaborators_by_author_name(author_name):
#     author_id = Authors.query.filter_by(name=author_name).first().id
#     res = []
#     for id in get_top_k_collaborators_by_author(author_id):
#         res.append(Authors.query.get_or_404(int(id)))
#     return jsonify(authors_schema.dump(res))

@app.route("/add_author", methods=['POST'])
def add_author():
    request_data = request.get_json()
    name = None
    org = None

    if "name" in request_data:
        name = request_data["name"]
    if "org" in request_data:
        org = request_data["org"]

    entry = Authors(name, org)
    db.session.add(entry)
    db.session.commit()
    return "Ok"


@app.route("/delete_author", methods=['POST'])
def delete_author():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        Authors.query.filter(Authors.id == id).delete()
        db.session.commit()

    return "Ok"


@app.route("/update_author", methods=['POST'])
def update_author():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        authors = Authors.query.filter(Authors.id == id)
        author_schema_fields = author_schema.get_fields()
        for param_name, param_value in request_data.items():
            if (param_name != "id") and (param_name in author_schema_fields):
                for author in authors:
                    setattr(author, param_name, param_value)

        db.session.commit()

    return "Ok"


# "author_paper" table methods
@app.route("/get_author_papers", methods=['GET'])
def get_author_papers():
    return jsonify(author_papers_schema.dump(AuthorPapers.query.all()))


@app.route("/get_author_paper/<int:id>", methods=['GET'])
def get_author_paper_by_id(id):
    return author_paper_schema.jsonify(AuthorPapers.query.get_or_404(int(id)))


@app.route("/add_author_paper", methods=['POST'])
def add_author_paper():
    request_data = request.get_json()
    paper_id = None
    author_id = None

    if "paper_id" in request_data:
        paper_id = int(request_data["paper_id"])
    if "author_id" in request_data:
        author_id = int(request_data["author_id"])

    entry = AuthorPapers(paper_id, author_id)
    db.session.add(entry)
    db.session.commit()
    return "Ok"


@app.route("/delete_author_paper", methods=['POST'])
def delete_author_paper():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        AuthorPapers.query.filter(AuthorPapers.id == id).delete()
        db.session.commit()

    return "Ok"


@app.route("/update_author_paper", methods=['POST'])
def update_author_paper():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        author_papers = AuthorPapers.query.filter(AuthorPapers.id == id)
        author_paper_schema_fields = author_paper_schema.get_fields()
        for param_name, param_value in request_data.items():
            if (param_name != "id") and (param_name in author_paper_schema_fields):
                for author_paper in author_papers:
                    setattr(author_paper, param_name, param_value)

        db.session.commit()

    return "Ok"


# "venues" table methods
@app.route("/get_venues", methods=['GET'])
def get_venues():
    return jsonify(venues_schema.dump(Venues.query.all()))


@app.route("/get_venue/<int:id>", methods=['GET'])
def get_venue_by_id(id):
    return venue_schema.jsonify(Venues.query.get_or_404(int(id)))


@app.route("/add_venue", methods=['POST'])
def add_venue():
    request_data = request.get_json()
    raw = None
    publisher = None
    issn = None
    isbn = None

    if "raw" in request_data:
        raw = request_data["raw"]
    if "publisher" in request_data:
        publisher = request_data["publisher"]
    if "issn" in request_data:
        issn = request_data["issn"]
    if "isbn" in request_data:
        isbn = request_data["isbn"]

    entry = Venues(raw, publisher, issn, isbn)
    db.session.add(entry)
    db.session.commit()
    return "Ok"


@app.route("/delete_venue", methods=['POST'])
def delete_venue():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        Venues.query.filter(Venues.id == id).delete()
        db.session.commit()

    return "Ok"


@app.route("/update_venue", methods=['POST'])
def update_venue():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        venues = Venues.query.filter(Venues.id == id)
        venue_schema_fields = venue_schema.get_fields()
        for param_name, param_value in request_data.items():
            if (param_name != "id") and (param_name in venue_schema_fields):
                for venue in venues:
                    setattr(venue, param_name, param_value)

        db.session.commit()

    return "Ok"


# "papers_refs" table methods
@app.route("/get_paper_refs", methods=['GET'])
def get_paper_refs():
    return jsonify(paper_references_schema.dump(PaperReferences.query.all()))


@app.route("/get_paper_ref/<int:id>", methods=['GET'])
def get_paper_ref_by_id(id):
    return paper_reference_schema.jsonify(PaperReferences.query.get_or_404(int(id)))


@app.route("/add_paper_refs", methods=['POST'])
def add_paper_references():
    request_data = request.get_json()
    parent_paper = None
    child_paper = None

    if "parent_paper" in request_data:
        parent_paper = int(request_data["parent_paper"])
    if "child_paper" in request_data:
        child_paper = int(request_data["child_paper"])

    entry = PaperReferences(parent_paper, child_paper)
    db.session.add(entry)
    db.session.commit()
    return "Ok"


@app.route("/delete_paper_refs", methods=['POST'])
def delete_paper_refs():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        PaperReferences.query.filter(PaperReferences.id == id).delete()
        db.session.commit()

    return "Ok"


@app.route("/update_paper_refs", methods=['POST'])
def update_paper_refs():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        paper_refs = PaperReferences.query.filter(PaperReferences.id == id)
        paper_refs_schema_fields = paper_reference_schema.get_fields()
        for param_name, param_value in request_data.items():
            if (param_name != "id") and (param_name in paper_refs_schema_fields):
                for paper_ref in paper_refs:
                    setattr(paper_ref, param_name, param_value)

        db.session.commit()

    return "Ok"


# "papers_tags" table methods
@app.route("/get_paper_tags", methods=['GET'])
def get_paper_tags():
    return jsonify(paper_tags_schema.dump(PaperTags.query.all()))


@app.route("/get_paper_tag/<int:id>", methods=['GET'])
def get_paper_tag_by_id(id):
    return paper_tag_schema.jsonify(PaperTags.query.get_or_404(int(id)))


@app.route("/add_paper_tags", methods=['POST'])
def add_paper_tags():
    request_data = request.get_json()
    paper_id = None
    tag_id = None

    if "paper_id" in request_data:
        paper_id = int(request_data["paper_id"])
    if "tag_id" in request_data:
        tag_id = int(request_data["tag_id"])

    entry = PaperTags(paper_id, tag_id)
    db.session.add(entry)
    db.session.commit()
    return "Ok"


@app.route("/delete_paper_tags", methods=['POST'])
def delete_paper_tags():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        PaperTags.query.filter(PaperTags.id == id).delete()
        db.session.commit()

    return "Ok"


@app.route("/update_paper_tags", methods=['POST'])
def update_paper_tags():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        paper_tags = PaperTags.query.filter(PaperTags.id == id)
        paper_tags_schema_fields = paper_tag_schema.get_fields()
        for param_name, param_value in request_data.items():
            if (param_name != "id") and (param_name in paper_tags_schema_fields):
                for paper_tag in paper_tags:
                    setattr(paper_tag, param_name, param_value)

        db.session.commit()

    return "Ok"


# "tags" table methods
@app.route("/get_tags", methods=['GET'])
def get_tags():
    return jsonify(tags_schema.dump(Tags.query.all()))


@app.route("/get_tag/<int:id>", methods=['GET'])
def get_tag_by_id(id):
    return tag_schema.jsonify(Tags.query.get_or_404(int(id)))


@app.route("/add_tags", methods=['POST'])
def add_tags():
    request_data = request.get_json()
    tag_name = None

    if "tag_name" in request_data:
        tag_name = request_data["tag_name"]

    entry = Tags(tag_name)
    db.session.add(entry)
    db.session.commit()
    return "Ok"


@app.route("/delete_tags", methods=['POST'])
def delete_tags():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        Tags.query.filter(Tags.id == id).delete()
        db.session.commit()

    return "Ok"


@app.route("/update_tags", methods=['POST'])
def update_tags():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        tags = Tags.query.filter(Tags.id == id)
        tags_schema_fields = tag_schema.get_fields()
        for param_name, param_value in request_data.items():
            if (param_name != "id") and (param_name in tags_schema_fields):
                for tag in tags:
                    setattr(tag, param_name, param_value)

        db.session.commit()

    return "Ok"


# "user" table methods
@app.route("/get_users", methods=['GET'])
def get_users():
    return jsonify(users_schema.dump(User.query.all()))


@app.route("/get_user/<int:id>", methods=['GET'])
def get_user_by_id(id):
    return user_schema.jsonify(User.query.get_or_404(int(id)))


@app.route("/user_exists", methods=['GET'])
def user_exists():
    request_data = request.get_json(force=True)
    user = User.query.filter_by(login=request_data["login"]).first()

    return json.dumps(bool(user))


@app.route("/login_user", methods=['GET'])
def login_user():
    request_data = request.get_json(force=True)
    user = User.query.filter_by(login=request_data["login"]).first_or_404()

    return json.dumps(user.password == request_data["password"])


@app.route("/add_users", methods=['POST'])
def add_users():
    request_data = request.get_json(force=True)
    login = None

    password = None

    if "login" in request_data:
        login = request_data["login"]
    if "password" in request_data:
        password = request_data["password"]

    entry = User(login, password)
    db.session.add(entry)
    db.session.commit()
    return "Ok"


@app.route("/delete_users", methods=['POST'])
def delete_users():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        User.query.filter(User.id == id).delete()
        db.session.commit()

    return "Ok"


@app.route("/update_users", methods=['POST'])
def update_users():
    request_data = request.get_json()
    if "id" in request_data:
        id = int(request_data["id"])
        users = User.query.filter(User.id == id)
        users_schema_fields = user_schema.get_fields()
        for param_name, param_value in request_data.items():
            if (param_name != "id") and (param_name in users_schema_fields):
                for user in users:
                    setattr(user, param_name, param_value)

        db.session.commit()

    return "Ok"


if __name__ == '__main__':
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
    except Exception as exp:
        print(f"Failed to create databases: {str(exp)}")
    app.run(debug=True, host='0.0.0.0')
