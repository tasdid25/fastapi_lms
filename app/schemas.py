from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PersonBase(BaseModel):
	first_name: str
	last_name: str


class StudentCreate(PersonBase):
	pass


class StudentRead(PersonBase):
	id: int
	created_at: datetime

	class Config:
		from_attributes = True


class TeacherCreate(PersonBase):
	pass


class TeacherRead(PersonBase):
	id: int
	created_at: datetime

	class Config:
		from_attributes = True


class CourseCreate(BaseModel):
	title: str
	capacity: int = 30
	teacher_id: Optional[int] = None


class CourseRead(BaseModel):
	id: int
	title: str
	capacity: int
	teacher_id: Optional[int]

	class Config:
		from_attributes = True


class EnrollmentCreate(BaseModel):
	student_id: int
	course_id: int


class EnrollmentRead(BaseModel):
	id: int
	student_id: int
	course_id: int
	created_at: datetime

	class Config:
		from_attributes = True


class ScrapedResourceCreate(BaseModel):
	source: str
	title: str
	url: str
	category_or_author: str
	price: Optional[str] = None


class ScrapedResourceRead(ScrapedResourceCreate):
	id: int
	created_at: datetime

	class Config:
		from_attributes = True