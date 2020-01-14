def init_app(app):
    from . import home, user, hydra_oauth2, hydra_integration, login, signup, account

    app.register_blueprint(home.bp, url_prefix='/')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(login.bp, url_prefix='/login')
    app.register_blueprint(signup.bp, url_prefix='/signup')
    app.register_blueprint(account.bp, url_prefix='/account')
    app.register_blueprint(hydra_oauth2.bp, url_prefix='/oauth2')
    app.register_blueprint(hydra_integration.bp, url_prefix='/hydra')
