"""
Database router for separating MoH and Platform databases.
Ensures MoH models use the independent moh_db database.
"""

class DatabaseRouter:
    """
    A router to control all database operations on models for different databases
    """
    
    moh_apps = {'moh'}
    platform_apps = {'customer', 'pharmacy', 'platform_admin', 'admin', 'auth', 'contenttypes', 'sessions'}

    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        if model._meta.app_label in self.moh_apps:
            return 'moh_db'
        elif model._meta.app_label in self.platform_apps:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        if model._meta.app_label in self.moh_apps:
            return 'moh_db'
        elif model._meta.app_label in self.platform_apps:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same app."""
        db_set = {'default', 'moh_db'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        if app_label in self.moh_apps:
            return db == 'moh_db'
        elif app_label in self.platform_apps:
            return db == 'default'
        elif db == 'moh_db':
            return False
        return None