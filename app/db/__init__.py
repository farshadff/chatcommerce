import logging

from sqlalchemy import create_engine, desc, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

Base = declarative_base()


class DatabaseDriver:
    def __init__(self, db_url):
        try:
            self.engine = create_engine(db_url)
            Base.metadata.create_all(self.engine)
            self.Session = scoped_session(sessionmaker(bind=self.engine, expire_on_commit=False))
        except Exception as e:
            logging.error("Could not connect to the database: %s", e)

    def create(self, obj):
        session = self.Session()
        try:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj.id
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"SQLAlchemyError occurred: {e}")
        except Exception as e:
            session.rollback()
            logging.error(f"An unexpected error occurred: {e}")
        finally:
            session.close()

    def query(self, model, filter_by=None, limit=None, offset=None, order_by=None, email_filter=False):
        session = self.Session()

        # default_order_by = desc(model.created_at) if hasattr(model, 'created_at') else desc(model.id)
        #
        # if not order_by:
        #     order_by = default_order_by
        query = session.query(model)

        if filter_by:
            query = query.filter_by(**filter_by)
        if email_filter:
            query = query.filter(
                or_(
                    model.email.ilike('%unlocked%'),
                    model.email.is_(None)
                )
            )
        query = query.order_by(order_by)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        return query.all()

    def filter_query(self, model, filters=None, limit=None, offset=None, order_by=None):
        session = self.Session()

        default_order_by = desc(model.created_at) if hasattr(model, 'created_at') else desc(model.id)

        if not order_by:
            order_by = default_order_by

        query = session.query(model).order_by(order_by)
        if filters:
            query = query.filter(*filters)

        return query.limit(limit).offset(offset).all()

    def update(self, model, filter_by, update_data):
        session = self.Session()
        try:
            # logging.info(f"Attempting to update {model.__name__} where {filter_by} with {update_data}")
            objs = session.query(model).filter_by(**filter_by).all()
            if not objs:
                logging.warning(f"No records found for {model.__name__} with filter {filter_by}")
                return
            for obj in objs:
                for key, value in update_data.items():
                    setattr(obj, key, value)
            session.commit()
            logging.info(f"Successfully updated {len(objs)} records for {model.__name__}")
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"SQLAlchemyError occurred while updating {model.__name__}: {e}")
        except Exception as e:
            session.rollback()
            logging.error(f"An unexpected error occurred while updating {model.__name__}: {e}")
        finally:
            session.close()

    def bulk_update(self, model, filter_by, update_data):
        session = self.Session()
        try:
            session.query(model).filter_by(**filter_by).update(update_data)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete(self, model, filter_by):
        session = self.Session()
        objs = session.query(model).filter_by(**filter_by).all()
        for obj in objs:
            session.delete(obj)
        session.commit()
        session.close()

DATABASE_URL = "postgresql://postgres:postgres@localhost/scms"  # PostgreSQL
# Instantiate separate database drivers for each database
DB = DatabaseDriver(DATABASE_URL)
