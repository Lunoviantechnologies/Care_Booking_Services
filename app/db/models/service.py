from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True)  # baby_care
    title = Column(String)  # Baby Care
    color = Column(String)  # UI color

    options = relationship(
        "ServiceOption", back_populates="service", cascade="all, delete"
    )
    fields = relationship(
        "ServiceField", back_populates="service", cascade="all, delete"
    )


class ServiceOption(Base):
    __tablename__ = "service_options"

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    name = Column(String)

    service = relationship("Service", back_populates="options")


class ServiceField(Base):
    __tablename__ = "service_fields"

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"))

    field_name = Column(String)  # allergies
    field_type = Column(String)  # text / checkbox

    service = relationship("Service", back_populates="fields")
