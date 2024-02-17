from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    second_name: Mapped[str] = mapped_column(nullable=False)
    middle_name: Mapped[str] = mapped_column(nullable=False)
    organisation: Mapped[str] = mapped_column(nullable=False)
    org_phone: Mapped[str] = mapped_column(nullable=False)
    personal_phone: Mapped[str] = mapped_column(nullable=False)

    def __str__(self):
        return (f"id: {self.id}\n"
                f"organisation: {self.organisation}\n"
                f"name: {self.name} {self.middle_name} {self.second_name}\n"
                f"organisation phone number: {self.org_phone}\n"
                f"personal phone number: {self.personal_phone}\n")
