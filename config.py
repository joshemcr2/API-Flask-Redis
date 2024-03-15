class Config:
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgres://npmktnqt:aMVQ28LM95VqgbG-SBar2nK6YONHBl26@kesavan.db.elephantsql.com/npmktnqt'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development': DevelopmentConfig,
}