from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, func
import random

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random")
def get_random_cafe():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe = random_cafe.to_dict())

@app.route("/all")
def get_all():
    all_cafes_ojb = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    all_cafes = [cafe_obj.to_dict() for cafe_obj in all_cafes_ojb]
    return jsonify(all_cafes)

@app.route("/search")
def get_cafe_at_location():
    location = request.args.get("loc")
    cafe_at_location_obj = db.session.execute(db.select(Cafe).where(func.lower(Cafe.location)==location.lower()).order_by(Cafe.name)).scalars().all()
    if cafe_at_location_obj:
        cafe_at_location = [cafe.to_dict() for cafe in cafe_at_location_obj]
        return jsonify(cafe_at_location)
    return jsonify({"error":{"Not Found": "Sorry, we don't have a cafe at that location."}})

@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        new_price = request.args.get("new_price")
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated the price.")
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})

@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def report_closed(cafe_id):
    api_key = request.args.get("api-key")
    print("2")
    if api_key == "TopSecret":
        cafe = db.session.get(Cafe, cafe_id)
        if cafe:
            print("should not be here")
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            print("got here")
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 401
    else:
        return jsonify(error="Sorry that is not allowed. Make sure you have the correct API_Key."), 404

if __name__ == '__main__':
    app.run(debug=True)
