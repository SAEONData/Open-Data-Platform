from flask import Blueprint, flash, render_template, redirect, url_for, request

from ..models import db
from ..models.user import User

bp = Blueprint('user', __name__)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        if not email:  # todo validate email address
            error = "Email is required."
        elif not password:  # todo validate password
            error = "Password is required."
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                error = "User {} is already registered.".format(email)

        if error is None:
            # todo generate password hash; set active=False initially, email must be confirmed
            user = User(email=email, password=password, active=True)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('hydra.login'))

        flash(error)

    return render_template('register.html')
