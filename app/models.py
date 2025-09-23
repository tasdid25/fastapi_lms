from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
	Integer,
	String,
	DateTime,
	ForeignKey,
	UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


# OOP Pillar: Abstraction & Inheritance
class Person(Base):
	__abstract__ = True

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	first_name: Mapped[str] = mapped_column(String(100))
	last_name: Mapped[str] = mapped_column(String(100))
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	# Encapsulation via properties
	@property
	def full_name(self) -> str:
		return f"{self.first_name} {self.last_name}"

	# Polymorphism: each subclass can implement its own role label
	def role_label(self) -> str:  # pragma: no cover - default implementation
		return "person"


class Student(Person):
	__tablename__ = "students"

	enrollments: Mapped[list[Enrollment]] = relationship(
		"Enrollment", back_populates="student", cascade="all, delete-orphan"
	)

	def role_label(self) -> str:
		return "student"


class Teacher(Person):
	__tablename__ = "teachers"

	courses: Mapped[list[Course]] = relationship(
		"Course", back_populates="teacher", cascade="all, delete-orphan"
	)

	def role_label(self) -> str:
		return "teacher"


class Course(Base):
	__tablename__ = "courses"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	title: Mapped[str] = mapped_column(String(200), unique=True, index=True)
	capacity: Mapped[int] = mapped_column(Integer, default=30)
	teacher_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teachers.id"))

	teacher: Mapped[Optional[Teacher]] = relationship("Teacher", back_populates="courses")
	enrollments: Mapped[list[Enrollment]] = relationship(
		"Enrollment", back_populates="course", cascade="all, delete-orphan"
	)


class Enrollment(Base):
	__tablename__ = "enrollments"
	__table_args__ = (
		UniqueConstraint("student_id", "course_id", name="uq_student_course"),
	)

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
	course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	student: Mapped[Student] = relationship("Student", back_populates="enrollments")
	course: Mapped[Course] = relationship("Course", back_populates="enrollments")


class ScrapedResource(Base):
	__tablename__ = "scraped_resources"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	source: Mapped[str] = mapped_column(String(50))  # books/quotes
	title: Mapped[str] = mapped_column(String(300))
	url: Mapped[str] = mapped_column(String(500))
	category_or_author: Mapped[str] = mapped_column(String(200))
	price: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)