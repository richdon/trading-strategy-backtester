from flask import current_app
from extensions import db
import click
from sqlalchemy import text


def recreate_database():
    """
    Drop all existing tables and recreate the database
    Useful for development environment
    """
    with current_app.app_context():
        # Drop all existing tables
        db.drop_all()

        # Create all tables
        db.create_all()

        # Create PostgreSQL extensions if needed
        db.session.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))

        # Create any additional indexes (if not created by SQLAlchemy)
        db.session.execute(text('''
            CREATE INDEX IF NOT EXISTS idx_backtest_results_portfolio 
            ON backtest_strategies ((backtest_results->>'final_portfolio_value'));
        '''))

        db.session.commit()
        print("Database recreated successfully.")


def init_db_commands(app):
    """Add CLI commands for database management"""

    @app.cli.command("recreate-db")
    def recreate_db_command():
        """Recreate the entire database"""
        if click.confirm('This will delete all data. Are you sure?', abort=True):
            recreate_database()
            click.echo("Database recreation complete.")

    @app.cli.command("create-extensions")
    def create_extensions():
        """Create required PostgreSQL extensions"""
        with app.app_context():
            db.session.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            db.session.commit()
            click.echo("PostgreSQL extensions created.")

    @app.cli.command("create-indexes")
    def create_indexes():
        """Create additional database indexes"""
        with app.app_context():
            # Create index on JSON field
            db.session.execute(text('''
                CREATE INDEX IF NOT EXISTS idx_backtest_results_portfolio 
                ON backtest_strategies ((backtest_results->>'final_portfolio_value'));
            '''))
            db.session.commit()
            click.echo("Additional indexes created.")
