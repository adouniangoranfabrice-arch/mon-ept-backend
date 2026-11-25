"""Tables SQLAlchemy (représentation en base des entités du domaine)."""
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class JourModele(Base):
    __tablename__ = "jours"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    libelle: Mapped[str]
    ordre: Mapped[int]
    actif: Mapped[bool] = mapped_column(default=True)


class HeureModele(Base):
    __tablename__ = "heures"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[str]
    heure_debut: Mapped[str]
    heure_fin: Mapped[str]


class ClasseModele(Base):
    __tablename__ = "classes"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    nom: Mapped[str]
    niveau: Mapped[str] = mapped_column(default="")
    effectif: Mapped[int | None]
    couleur: Mapped[str]


class EleveModele(Base):
    __tablename__ = "eleves"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    nom_prenoms: Mapped[str]
    classe_id: Mapped[str] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"), index=True)


class EvaluationModele(Base):
    __tablename__ = "evaluations"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    classe_id: Mapped[str] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"), index=True)
    trimestre: Mapped[int]
    libelle: Mapped[str]
    date: Mapped[str] = mapped_column(default="")
    bareme: Mapped[float] = mapped_column(default=20)
    coefficient: Mapped[float] = mapped_column(default=1)


class NoteModele(Base):
    __tablename__ = "notes"
    __table_args__ = (UniqueConstraint("evaluation_id", "eleve_id", name="uq_note_eleve"),)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("evaluations.id", ondelete="CASCADE"), index=True)
    eleve_id: Mapped[str] = mapped_column(ForeignKey("eleves.id", ondelete="CASCADE"), index=True)
    valeur: Mapped[float]


class SeanceModele(Base):
    __tablename__ = "seances"
    __table_args__ = (UniqueConstraint("jour_id", "heure_id", name="uq_seance_creneau"),)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    jour_id: Mapped[str] = mapped_column(ForeignKey("jours.id", ondelete="CASCADE"))
    heure_id: Mapped[str] = mapped_column(ForeignKey("heures.id", ondelete="CASCADE"))
    classe_id: Mapped[str] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"))
    salle: Mapped[str] = mapped_column(default="")
    recurrente: Mapped[bool] = mapped_column(default=True)


MODELES = {
    "jours": JourModele, "heures": HeureModele, "classes": ClasseModele, "eleves": EleveModele,
    "evaluations": EvaluationModele, "notes": NoteModele, "seances": SeanceModele,
}
