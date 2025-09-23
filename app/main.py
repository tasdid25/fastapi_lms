from __future__ import annotations

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .db import get_session, init_db
from . import crud, schemas

app = FastAPI(title="School Management System (SMS)")
# Root
@app.get("/")
def root():
	return RedirectResponse(url="/docs", status_code=307)


@app.on_event("startup")
def _startup():
	init_db()


# Students
@app.post("/students", response_model=schemas.StudentRead)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_session)):
	return crud.create_student(db, student)


@app.get("/students", response_model=list[schemas.StudentRead])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
	return crud.list_students(db, skip, limit)


@app.get("/students/{student_id}", response_model=schemas.StudentRead)
def get_student(student_id: int, db: Session = Depends(get_session)):
	obj = crud.get_student(db, student_id)
	if not obj:
		raise HTTPException(status_code=404, detail="Student not found")
	return obj


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_session)):
	ok = crud.delete_student(db, student_id)
	if not ok:
		raise HTTPException(status_code=404, detail="Student not found")
	return {"deleted": True}


# Teachers
@app.post("/teachers", response_model=schemas.TeacherRead)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_session)):
	return crud.create_teacher(db, teacher)


@app.get("/teachers", response_model=list[schemas.TeacherRead])
def list_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
	return crud.list_teachers(db, skip, limit)


@app.get("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
def get_teacher(teacher_id: int, db: Session = Depends(get_session)):
	obj = crud.get_teacher(db, teacher_id)
	if not obj:
		raise HTTPException(status_code=404, detail="Teacher not found")
	return obj


@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_session)):
	ok = crud.delete_teacher(db, teacher_id)
	if not ok:
		raise HTTPException(status_code=404, detail="Teacher not found")
	return {"deleted": True}


# Courses
@app.post("/courses", response_model=schemas.CourseRead)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_session)):
	return crud.create_course(db, course)


@app.get("/courses", response_model=list[schemas.CourseRead])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
	return crud.list_courses(db, skip, limit)


@app.get("/courses/{course_id}", response_model=schemas.CourseRead)
def get_course(course_id: int, db: Session = Depends(get_session)):
	obj = crud.get_course(db, course_id)
	if not obj:
		raise HTTPException(status_code=404, detail="Course not found")
	return obj


@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_session)):
	ok = crud.delete_course(db, course_id)
	if not ok:
		raise HTTPException(status_code=404, detail="Course not found")
	return {"deleted": True}


# Enrollments
@app.post("/enrollments", response_model=schemas.EnrollmentRead)
def create_enrollment(enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_session)):
	try:
		return crud.create_enrollment(db, enrollment)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@app.get("/enrollments", response_model=list[schemas.EnrollmentRead])
def list_enrollments(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
	return crud.list_enrollments(db, skip, limit)


@app.delete("/enrollments/{enrollment_id}")
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_session)):
	ok = crud.delete_enrollment(db, enrollment_id)
	if not ok:
		raise HTTPException(status_code=404, detail="Enrollment not found")
	return {"deleted": True}


# Scraped resources import
@app.post("/scraped/import")
def import_scraped(items: list[schemas.ScrapedResourceCreate], db: Session = Depends(get_session)):
	inserted = crud.insert_scraped_resources(db, items)
	return {"inserted": inserted}