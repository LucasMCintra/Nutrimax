from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Client, Goal, Meal


def test_models_can_be_persisted_in_sqlite() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        client = Client(
            name="Pessoa Teste",
            weight=Decimal("70.50"),
            height=Decimal("1.75"),
            age=30,
            goal=Goal(description="Manter peso"),
            meals=[Meal(meal_date=date(2026, 1, 1), image_url="meal.jpg")],
        )
        session.add(client)
        session.commit()

        saved_client = session.query(Client).one()
        assert saved_client.goal.description == "Manter peso"
        assert saved_client.meals[0].meal_date == date(2026, 1, 1)
