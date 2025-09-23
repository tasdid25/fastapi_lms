from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import init_db


client = TestClient(app)


def setup_module():
	init_db()


def create_student(first="John", last="Doe"):
	resp = client.post("/students", json={"first_name": first, "last_name": last})
	assert resp.status_code == 200
	return resp.json()["id"]


def create_teacher(first="Jane", last="Smith"):
	resp = client.post("/teachers", json={"first_name": first, "last_name": last})
	assert resp.status_code == 200
	return resp.json()["id"]


def create_course(title="Math 101", capacity=1, teacher_id=None):
	resp = client.post("/courses", json={"title": title, "capacity": capacity, "teacher_id": teacher_id})
	assert resp.status_code == 200
	return resp.json()["id"]


def test_enrollment_rules_duplicate_and_capacity():
	teacher_id = create_teacher()
	course_id = create_course(capacity=1, teacher_id=teacher_id)
	student_a = create_student("Alice", "A")
	student_b = create_student("Bob", "B")

	# First enrollment ok
	resp1 = client.post("/enrollments", json={"student_id": student_a, "course_id": course_id})
	assert resp1.status_code == 200

	# Duplicate enrollment
	resp_dup = client.post("/enrollments", json={"student_id": student_a, "course_id": course_id})
	assert resp_dup.status_code == 400
	assert "already" in resp_dup.json()["detail"].lower()

	# Capacity reached for second student
	resp_cap = client.post("/enrollments", json={"student_id": student_b, "course_id": course_id})
	assert resp_cap.status_code == 400
	assert "capacity" in resp_cap.json()["detail"].lower()