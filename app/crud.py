from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from . import models, schemas


# Students

def create_student(db: Session, data: schemas.StudentCreate) -> models.Student:
	student = models.Student(first_name=data.first_name, last_name=data.last_name)
	db.add(student)
	db.commit()
	db.refresh(student)
	return student


def get_student(db: Session, student_id: int) -> models.Student | None:
	return db.get(models.Student, student_id)


def list_students(db: Session, skip: int = 0, limit: int = 100) -> list[models.Student]:
	return db.execute(select(models.Student).offset(skip).limit(limit)).scalars().all()


def delete_student(db: Session, student_id: int) -> bool:
	student = get_student(db, student_id)
	if not student:
		return False
	db.delete(student)
	db.commit()
	return True


# Teachers

def create_teacher(db: Session, data: schemas.TeacherCreate) -> models.Teacher:
	teacher = models.Teacher(first_name=data.first_name, last_name=data.last_name)
	db.add(teacher)
	db.commit()
	db.refresh(teacher)
	return teacher


def get_teacher(db: Session, teacher_id: int) -> models.Teacher | None:
	return db.get(models.Teacher, teacher_id)


def list_teachers(db: Session, skip: int = 0, limit: int = 100) -> list[models.Teacher]:
	return db.execute(select(models.Teacher).offset(skip).limit(limit)).scalars().all()


def delete_teacher(db: Session, teacher_id: int) -> bool:
	teacher = get_teacher(db, teacher_id)
	if not teacher:
		return False
	db.delete(teacher)
	db.commit()
	return True


# Courses

def create_course(db: Session, data: schemas.CourseCreate) -> models.Course:
	course = models.Course(title=data.title, capacity=data.capacity, teacher_id=data.teacher_id)
	db.add(course)
	db.commit()
	db.refresh(course)
	return course


def get_course(db: Session, course_id: int) -> models.Course | None:
	return db.get(models.Course, course_id)


def list_courses(db: Session, skip: int = 0, limit: int = 100) -> list[models.Course]:
	return db.execute(select(models.Course).offset(skip).limit(limit)).scalars().all()


def delete_course(db: Session, course_id: int) -> bool:
	course = get_course(db, course_id)
	if not course:
		return False
	db.delete(course)
	db.commit()
	return True


# Enrollments with business rules

def create_enrollment(db: Session, data: schemas.EnrollmentCreate) -> models.Enrollment:
	# Prevent duplicates
	exists = db.execute(
		select(models.Enrollment).where(
			models.Enrollment.student_id == data.student_id,
			models.Enrollment.course_id == data.course_id,
		)
	).scalar_one_or_none()
	if exists:
		raise ValueError("Student already enrolled in this course")

	# Enforce capacity
	count = db.execute(
		select(func.count(models.Enrollment.id)).where(
			models.Enrollment.course_id == data.course_id
		)
	).scalar_one()
	course = get_course(db, data.course_id)
	if course is None:
		raise ValueError("Course not found")
	if count >= course.capacity:
		raise ValueError("Course capacity reached")

	enrollment = models.Enrollment(student_id=data.student_id, course_id=data.course_id)
	db.add(enrollment)
	db.commit()
	db.refresh(enrollment)
	return enrollment


def list_enrollments(db: Session, skip: int = 0, limit: int = 100) -> list[models.Enrollment]:
	return db.execute(select(models.Enrollment).offset(skip).limit(limit)).scalars().all()


def delete_enrollment(db: Session, enrollment_id: int) -> bool:
	enrollment = db.get(models.Enrollment, enrollment_id)
	if not enrollment:
		return False
	db.delete(enrollment)
	db.commit()
	return True


# Scraped resource insert

def insert_scraped_resources(db: Session, items: list[schemas.ScrapedResourceCreate]) -> int:
	objects = [
		models.ScrapedResource(
			source=i.source,
			title=i.title,
			url=i.url,
			category_or_author=i.category_or_author,
			price=i.price,
		)
		for i in items
	]
	db.add_all(objects)
	db.commit()
	return len(objects)