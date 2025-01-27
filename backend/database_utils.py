from flask import current_app
from extensions import db
import click


def recreate_database():
    """
    Drop all existing tables and recreate the database
    Useful for development environment
    """
    with current_app.app_context():
        # Drop all existing tables
        db.drop_all()

        # Create all tables based on models
        db.create_all()

        print("Database recreated successfully.")


def init_db_commands(app):
    """
    Add CLI commands for database management
    """

    @app.cli.command("recreate-db")
    def recreate_db_command():
        """Recreate the entire database"""
        recreate_database()
        click.echo("Database recreation complete.")

    @app.cli.command("init-db")
    def initialize_database():
        """Initialize the database with base tables"""
        recreate_database()
        click.echo("Database initialized.")