
from sqlalchemy import func, select


from database.models import Quote, Author, Tag, quote_tag_association


def top_ten_tags(db):
    tags = db.session.query(Tag.name, func.count(Quote.id)) \
        .join(Tag.quotes) \
        .group_by(Tag.name) \
        .order_by(func.count(Quote.id).desc()) \
        .limit(10) \
        .all()
    return tags


def get_author(db, author_name):
    return db.session.query(Author)\
        .filter(Author.fullname == author_name)\
        .first()


def get_all_quotes(db):
    return db.select(Quote).order_by(Quote.id)


def get_all_authors(db):
    return db.session.query(Author).all()


def get_all_tags(db):
    return db.session.query(Tag).all()


def get_quotes_by_tag(db, tag_name):
    return db.select(Quote).join(Quote.tags).filter(Tag.name == tag_name)


def add_quote_db(db, author_name, quote_text, tags_list):
    this_author = db.session.query(Author).where(Author.fullname == author_name).first()
    this_quote = quote_text
    this_tags = list(db.session.scalars(select(Tag).where(Tag.name.in_(tags_list))))

    quote = Quote(author_id=this_author.id,
                  quote=this_quote,
                  tags=this_tags)
    db.session.add(quote)
    db.session.commit()


def add_author_db(db, fullname, born_date, born_location, description):
    author = Author(fullname=fullname,
                    born_date=born_date,
                    born_location=born_location,
                    description=description)
    db.session.add(author)
    db.session.commit()


def add_tag_db(db, tag_name):
    tag = Tag(name=tag_name)
    db.session.add(tag)
    db.session.commit()


def paginate_quotes(db, page_num, quotes):
    return db.paginate(quotes, page=page_num, per_page=10, max_per_page=10)


def del_all_records(db):
    db.session.execute(quote_tag_association.delete())
    db.session.execute(Quote.__table__.delete())
    db.session.execute(Author.__table__.delete())
    db.session.execute(Tag.__table__.delete())
    db.session.commit()
